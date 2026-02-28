def build_lineage():

    import sys
    import os
    import clr
    import re
    import pandas as pd
    import networkx as nx

    # --------------------------------------------------
    # LOAD ADOMD.NET
    # --------------------------------------------------

    dll_path = r"C:\Program Files\Microsoft.NET\ADOMD.NET\160\Microsoft.AnalysisServices.AdomdClient.dll"
    dll_folder = os.path.dirname(dll_path)

    sys.path.append(dll_folder)
    os.environ["PATH"] = dll_folder + ";" + os.environ["PATH"]

    clr.AddReference(dll_path)

    from pyadomd import Pyadomd

    # --------------------------------------------------
    # CONNECTION STRING
    # --------------------------------------------------

    conn_str = """
    Provider=MSOLAP;
    Data Source=powerbi://api.powerbi.com/v1.0/myorg/Lease%20Activity;
    Initial Catalog=Lease Activity;
    """

    with Pyadomd(conn_str) as conn:

        def run_query(query):
            with conn.cursor().execute(query) as cur:
                rows = cur.fetchall()
                cols = [col[0] for col in cur.description]
            return pd.DataFrame(rows, columns=cols)

        df_tables = run_query("SELECT * FROM $SYSTEM.TMSCHEMA_TABLES")
        df_columns = run_query("SELECT * FROM $SYSTEM.TMSCHEMA_COLUMNS")
        df_measures = run_query("SELECT * FROM $SYSTEM.TMSCHEMA_MEASURES")
        df_partitions = run_query("SELECT * FROM $SYSTEM.TMSCHEMA_PARTITIONS")
        df_relationships = run_query("SELECT * FROM $SYSTEM.TMSCHEMA_RELATIONSHIPS")

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    def get_name_column(df):
        return "Name" if "Name" in df.columns else "ExplicitName"

    table_name_col = get_name_column(df_tables)
    column_name_col = get_name_column(df_columns)
    measure_name_col = get_name_column(df_measures)

    table_lookup = dict(zip(df_tables["ID"], df_tables[table_name_col]))

    df_columns["TableName"] = df_columns["TableID"].map(table_lookup)
    df_measures["TableName"] = df_measures["TableID"].map(table_lookup)
    df_partitions["TableName"] = df_partitions["TableID"].map(table_lookup)

    df_measures["Expression"] = df_measures["Expression"].fillna("")
    df_columns["Expression"] = df_columns["Expression"].fillna("")

    lineage_rows = []

    # --------------------------------------------------
    # MEASURE LOOKUP
    # --------------------------------------------------

    measure_lookup = {
        row[measure_name_col]: row["TableName"]
        for _, row in df_measures.iterrows()
    }

    # --------------------------------------------------
    # DAX DEPENDENCY PARSER
    # --------------------------------------------------

    def extract_dependencies(expression):

        if not expression:
            return [], []

        pattern = r'([\w\s]*)\[(.*?)\]'
        matches = re.findall(pattern, expression)

        column_refs = []
        measure_refs = []

        for table, name in matches:
            if table.strip():
                column_refs.append((table.strip(), name.strip()))
            else:
                measure_refs.append(name.strip())

        return column_refs, measure_refs

    # --------------------------------------------------
    # MEASURE LINEAGE
    # --------------------------------------------------

    for _, row in df_measures.iterrows():

        expr = row["Expression"]
        measure_name = row[measure_name_col]
        current_table = row["TableName"]

        col_refs, measure_refs = extract_dependencies(expr)

        for table, column in col_refs:
            resolved_table = table if table else current_table

            lineage_rows.append({
                "Source": f"{resolved_table}.{column}",
                "Target": f"{current_table}.{measure_name}",
                "Transformation": expr,
                "DependencyType": "Column Reference"
            })

        for measure in measure_refs:
            source_table = measure_lookup.get(measure, current_table)

            lineage_rows.append({
                "Source": f"{source_table}.{measure}",
                "Target": f"{current_table}.{measure_name}",
                "Transformation": expr,
                "DependencyType": "Measure Reference"
            })

    # --------------------------------------------------
    # CALCULATED COLUMN LINEAGE
    # --------------------------------------------------

    calc_columns = df_columns[df_columns["Expression"] != ""]

    for _, row in calc_columns.iterrows():

        expr = row["Expression"]
        calc_name = row[column_name_col]
        current_table = row["TableName"]

        col_refs, measure_refs = extract_dependencies(expr)

        for table, column in col_refs:
            resolved_table = table if table else current_table

            dep_type = "RELATED Relationship" if "RELATED" in expr.upper() else "Column Reference"

            lineage_rows.append({
                "Source": f"{resolved_table}.{column}",
                "Target": f"{current_table}.{calc_name}",
                "Transformation": expr,
                "DependencyType": dep_type
            })

        for measure in measure_refs:
            source_table = measure_lookup.get(measure, current_table)

            lineage_rows.append({
                "Source": f"{source_table}.{measure}",
                "Target": f"{current_table}.{calc_name}",
                "Transformation": expr,
                "DependencyType": "Measure Reference"
            })

    # --------------------------------------------------
    # MODEL RELATIONSHIPS
    # --------------------------------------------------

    for _, row in df_relationships.iterrows():

        from_table = table_lookup[row["FromTableID"]]
        to_table = table_lookup[row["ToTableID"]]

        lineage_rows.append({
            "Source": from_table,
            "Target": to_table,
            "Transformation": "Model Relationship",
            "DependencyType": "Model Relationship"
        })

    # --------------------------------------------------
    # ROBUST M SOURCE EXTRACTION
    # --------------------------------------------------

    def extract_m_sources(m_code):

        if not m_code:
            return []

        sources = []

        # If JSON wrapped
        json_query_pattern = r'"Query"\s*:\s*"([^"]+)"'
        json_match = re.search(json_query_pattern, m_code, flags=re.IGNORECASE | re.DOTALL)
        if json_match:
            m_code = json_match.group(1)

        # NativeQuery SQL
        native_query_pattern = r'Value\.NativeQuery\([^,]+,\s*"([^"]+)"'
        native_match = re.search(native_query_pattern, m_code, flags=re.IGNORECASE | re.DOTALL)

        if native_match:
            sql = native_match.group(1)
            from_pattern = r'FROM\s+([\[\]\w\.]+)'
            from_match = re.search(from_pattern, sql, flags=re.IGNORECASE)
            if from_match:
                table = from_match.group(1).replace("[", "").replace("]", "")
                return [table]

        # Sql.Database navigation
        nav_pattern = r'\[Schema="([^"]+)",\s*Item="([^"]+)"\]'
        nav_matches = re.findall(nav_pattern, m_code)

        for schema, item in nav_matches:
            sources.append(f"{schema}.{item}")

        # Fallback simple Item=
        fallback_pattern = r'Item="([^"]+)"'
        fallback_matches = re.findall(fallback_pattern, m_code)

        for item in fallback_matches:
            sources.append(item)

        return list(set(sources))

    for _, row in df_partitions.iterrows():

        table_name = row["TableName"]
        m_expression = row.get("Expression", "") or row.get("QueryDefinition", "")

        base_sources = extract_m_sources(m_expression)

        for src in base_sources:
            lineage_rows.append({
                "Source": f"SQL.{src}",
                "Target": table_name,
                "Transformation": "Power Query Source",
                "DependencyType": "Source Mapping"
            })

    # --------------------------------------------------
    # BUILD GRAPH
    # --------------------------------------------------

    df_lineage = pd.DataFrame(lineage_rows)

    G = nx.DiGraph()

    for _, row in df_lineage.iterrows():
        G.add_edge(
            row["Source"],
            row["Target"],
            transformation=row.get("Transformation", ""),
            dependency=row.get("DependencyType", "")
        )

    return df_lineage, G