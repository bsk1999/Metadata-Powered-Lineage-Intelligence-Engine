import pandas as pd
import sqlglot
import re
from sqlglot.expressions import Select, Alias, Column


def extract_column_usage(sql_text, source_column):
    """
    Extract column transformations where source_column is used.
    """

    lineage = []

    try:
        parsed = sqlglot.parse_one(sql_text, read="tsql")

        for select in parsed.find_all(Select):

            for expression in select.expressions:

                # Case 1: Expression with alias
                if isinstance(expression, Alias):

                    alias_name = expression.alias
                    inner_expr = expression.this

                    used_columns = [
                        col.name.upper()
                        for col in inner_expr.find_all(Column)
                    ]

                    if source_column.upper() in used_columns:
                        lineage.append({
                            "object_column": alias_name,
                            "transformation": inner_expr.sql()
                        })

                # Case 2: Direct column
                elif isinstance(expression, Column):

                    if expression.name.upper() == source_column.upper():
                        lineage.append({
                            "object_column": expression.name,
                            "transformation": expression.sql()
                        })

    except Exception:
        pass

    return lineage


def extract_insert_target(sql_text):
    """
    Extract INSERT INTO target schema and table using regex.
    """

    match = re.search(
        r"INSERT\s+INTO\s+\[?(\w+)\]?\.\[?(\w+)\]?",
        sql_text,
        re.IGNORECASE
    )

    if match:
        return match.group(1), match.group(2)

    return None, None


def get_full_column_lineage(conn, schema, table, column):
    """
    Returns full column-level lineage for given ODS table + column
    """

    query = f"""
    SELECT
        s.name AS schema_name,
        o.name AS object_name,
        o.type_desc,
        m.definition
    FROM sys.sql_modules m
    JOIN sys.objects o ON m.object_id = o.object_id
    JOIN sys.schemas s ON o.schema_id = s.schema_id
    WHERE m.definition LIKE '%{table}%'
    """

    df = pd.read_sql(query, conn)

    results = []

    for _, row in df.iterrows():

        sql_text = row["definition"]
        object_schema = row["schema_name"]
        object_name = row["object_name"]
        object_type = row["type_desc"]

        column_usages = extract_column_usage(sql_text, column)

        for usage in column_usages:

            # Add Procedure / View row
            results.append({
                "ODS_Table": f"{schema}.{table}",
                "ODS_Column": column,
                "Object_Name": f"{object_schema}.{object_name}",
                "Object_Type": object_type,
                "Object_Column": usage["object_column"],
                "Transformation": usage["transformation"]
            })

            # If procedure → also add target TABLE row
            if object_type == "SQL_STORED_PROCEDURE":

                target_schema, target_table = extract_insert_target(sql_text)

                if target_schema and target_table:

                    results.append({
                        "ODS_Table": f"{schema}.{table}",
                        "ODS_Column": column,
                        "Object_Name": f"{target_schema}.{target_table}",
                        "Object_Type": "TABLE",
                        "Object_Column": usage["object_column"],
                        "Transformation": usage["transformation"]
                    })

    # Remove duplicates if any
    result_df = pd.DataFrame(results).drop_duplicates()

    return result_df