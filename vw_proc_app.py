import streamlit as st
import pyodbc
import sqlglot
from sqlglot import parse, exp
import pandas as pd
import re
def run():
    # ==========================================================
    # STREAMLIT UI HEADER
    # ==========================================================
    st.set_page_config(page_title="Synapse Column Lineage", layout="wide")
    st.title("🔍 Synapse Column-Level Lineage (Views + Stored Procedures)")

    # ==========================================================
    # CONNECTION SECTION (Same logic as your script)
    # ==========================================================
    server = "syn-dlr-eda-prd.sql.azuresynapse.net"
    database = "Syndw"

    @st.cache_resource
    def get_connection(server, database):
        conn_str = f"""
        DRIVER={{ODBC Driver 18 for SQL Server}};
        SERVER={server};
        DATABASE={database};
        Authentication=ActiveDirectoryInteractive;
        Encrypt=yes;
        """
        return pyodbc.connect(conn_str)

    try:
        conn = get_connection(server, database)
        cursor = conn.cursor()
        st.success("✅ Connected to Synapse")
    except Exception as e:
        st.error(f"Connection failed: {e}")
        st.stop()

    # ==========================================================
    # FETCH OBJECTS (UNCHANGED QUERY)
    # ==========================================================
    object_query = """
    SELECT 
        s.name AS schema_name,
        o.name AS object_name,
        o.type_desc,
        m.definition
    FROM sys.objects o
    JOIN sys.schemas s ON o.schema_id = s.schema_id
    JOIN sys.sql_modules m ON o.object_id = m.object_id
    WHERE o.type IN ('V','P')
    AND o.name in ('VW_BLDG_METRICS','USP_LOAD_DMA_BLDG_METRICS','USP_LOAD_BLDG_METRICS')
    ORDER BY s.name, o.name
    """

    objects_df = pd.read_sql(object_query, conn)

    if objects_df.empty:
        st.warning("No objects found.")
        st.stop()

    # ==========================================================
    # INSTANT REACTIVE SEARCH + MULTISELECT (NO LAG VERSION)
    # ==========================================================

    objects_df["display_name"] = objects_df.apply(
        lambda x: f"{x['schema_name']}.{x['object_name']} ({x['type_desc']})",
        axis=1
    )

    st.subheader("📂 Select Objects")

    # --- Search box (no manual session assignment) ---
    search_text = st.text_input(
        "Search (LIKE / Contains)",
        placeholder="Type part of view or procedure name...",
        key="search_text"
    )

    # --- Apply filter immediately ---
    if search_text:
        filtered_df = objects_df[
            objects_df["display_name"].str.contains(
                search_text,
                case=False,
                na=False
            )
        ]
    else:
        filtered_df = objects_df.copy()

    filtered_options = filtered_df["display_name"].tolist()

    # --- Initialize selection state ---
    if "selected_objects" not in st.session_state:
        st.session_state.selected_objects = []

    # --- Remove selections not in filtered list ---
    st.session_state.selected_objects = [
        obj for obj in st.session_state.selected_objects
        if obj in filtered_options
    ]

    # --- Multiselect ---
    st.multiselect(
        "Choose View(s) / Stored Procedure(s)",
        options=filtered_options,
        key="selected_objects"
    )

    target_column_search = st.text_input(
        "🔎 Search Target Column (LIKE / Contains)",
        placeholder="Type part of target column name...",
        key="target_column_search"
    )

    # ==========================================================
    # CLEAN SQL (UNCHANGED)
    # ==========================================================
    def clean_sql(sql):
        sql = re.sub(r'--.*', '', sql)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.S)
        return sql.strip()

    # ==========================================================
    # PROCESS SELECT (UNCHANGED)
    # ==========================================================
    def process_select(select_stmt, target_table, object_name, object_type):

        results = []
        alias_map = {}

        for table in select_stmt.find_all(exp.Table):
            table_name = table.name
            schema = table.args.get("db")
            full_name = f"{schema}.{table_name}" if schema else table_name
            alias = table.alias or table_name
            alias_map[alias] = full_name

        for projection in select_stmt.expressions:

            target_column = projection.alias_or_name
            transformation = projection.sql(dialect="tsql")

            source_columns = []

            for col in projection.find_all(exp.Column):
                source_table = alias_map.get(col.table, col.table)
                source_columns.append(f"{source_table}.{col.name}")

            results.append({
                "object_name": object_name,
                "object_type": object_type,
                "target_table": target_table,
                "target_column": target_column,
                "source_columns": ", ".join(set(source_columns)),
                "transformation": transformation
            })

        return results


    # ==========================================================
    # MAIN EXTRACTION (YOUR LOGIC — 100% UNCHANGED)
    # ==========================================================
    if st.session_state.selected_objects:

        if not st.session_state.selected_objects:
            st.warning("Please select at least one object.")
        else:

            all_lineage = []

            for selected_display in st.session_state.selected_objects:
                selected_row = objects_df[
                    objects_df["display_name"] == selected_display
                ].iloc[0]

                schema_name = selected_row.schema_name
                object_name = selected_row.object_name
                object_type = selected_row.type_desc
                definition = clean_sql(selected_row.definition)

                try:
                    statements = parse(definition, read="tsql")
                except:
                    continue

            # 👇 your FULL lineage logic continues unchanged

                for statement in statements:
                    for node in statement.walk():


                        # ==================================================
                        # VIEWS
                        # ==================================================
                        if object_type == "VIEW" and isinstance(node, exp.Select):

                            target_table = f"{schema_name}.{object_name}"

                            results = process_select(
                                node,
                                target_table,
                                f"{schema_name}.{object_name}",
                                object_type
                            )

                            all_lineage.extend(results)

                        # ==================================================
                        # INSERT
                        # ==================================================
                        if isinstance(node, exp.Insert):

                            target_table = node.this.sql()
                            select_stmt = node.args.get("expression")

                            if isinstance(select_stmt, exp.Select):

                                results = process_select(
                                    select_stmt,
                                    target_table,
                                    f"{schema_name}.{object_name}",
                                    object_type
                                )

                                all_lineage.extend(results)

                        # ==================================================
                        # MERGE (UNCHANGED — YOUR FULL LOGIC)
                        # ==================================================
                        if isinstance(node, exp.Merge):

                            target_table = node.this.sql()
                            using = node.args.get("using")

                            subquery_map = {}
                            using_alias = None

                            if using:
                                using_alias = using.alias

                                if isinstance(using.this, exp.Select):
                                    for proj in using.this.expressions:
                                        subquery_map[proj.alias_or_name] = proj

                            # -------- UPDATE --------
                            for update in node.find_all(exp.Update):

                                for assignment in update.expressions:

                                    target_column = assignment.this.sql()
                                    rhs = assignment.expression
                                    transformation = rhs.sql()

                                    source_columns = []

                                    for col in rhs.find_all(exp.Column):

                                        if col.table == using_alias:

                                            resolved_expr = subquery_map.get(col.name)

                                            if resolved_expr:

                                                inner_columns = list(resolved_expr.find_all(exp.Column))

                                                if inner_columns:
                                                    for inner_col in inner_columns:
                                                        source_columns.append(
                                                            f"{inner_col.table}.{inner_col.name}"
                                                        )
                                                else:
                                                    source_columns.append(
                                                        resolved_expr.sql(dialect="tsql")
                                                    )
                                            else:
                                                source_columns.append(col.sql())
                                        else:
                                            source_columns.append(f"{col.table}.{col.name}")

                                    if not source_columns:
                                        source_columns.append(transformation)

                                    all_lineage.append({
                                        "object_name": f"{schema_name}.{object_name}",
                                        "object_type": object_type,
                                        "target_table": target_table,
                                        "target_column": target_column,
                                        "source_columns": ", ".join(set(source_columns)),
                                        "transformation": transformation
                                    })

                            # -------- INSERT (MERGE) --------
                            for insert in node.find_all(exp.Insert):

                                columns = insert.args.get("columns")
                                values = insert.args.get("expression")

                                if columns and isinstance(values, exp.Tuple):

                                    for target_col, value_expr in zip(columns, values.expressions):

                                        transformation = value_expr.sql()
                                        source_columns = []

                                        for col in value_expr.find_all(exp.Column):

                                            if col.table == using_alias:

                                                resolved_expr = subquery_map.get(col.name)

                                                if resolved_expr:

                                                    inner_columns = list(resolved_expr.find_all(exp.Column))

                                                    if inner_columns:
                                                        for inner_col in inner_columns:
                                                            source_columns.append(
                                                                f"{inner_col.table}.{inner_col.name}"
                                                            )
                                                    else:
                                                        source_columns.append(
                                                            resolved_expr.sql(dialect="tsql")
                                                        )
                                                else:
                                                    source_columns.append(col.sql())
                                            else:
                                                source_columns.append(f"{col.table}.{col.name}")

                                        if not source_columns:
                                            source_columns.append(transformation)

                                        all_lineage.append({
                                            "object_name": f"{schema_name}.{object_name}",
                                            "object_type": object_type,
                                            "target_table": target_table,
                                            "target_column": target_col.sql(),
                                            "source_columns": ", ".join(set(source_columns)),
                                            "transformation": transformation
                                        })

        # ==========================================================
        # DISPLAY (Only change: print → Streamlit)
        # ==========================================================
        df = pd.DataFrame(all_lineage)

        st.subheader("📊 Column Level Lineage")

        # Apply target column filter interactively
        if target_column_search:
            df = df[
                df["target_column"].str.contains(
                    target_column_search,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Download CSV",
            csv,
            file_name="synapse_column_lineage.csv",
            mime="text/csv"
        )
