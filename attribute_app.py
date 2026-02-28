import streamlit as st
import pandas as pd
from graphviz import Digraph

from db_connection import get_connection
from lineage_service import get_full_column_lineage

def run():
    # -------------------------------------------------
    # PAGE CONFIG
    # -------------------------------------------------
    st.set_page_config(
        page_title="Column Level Lineage Explorer",
        layout="wide"
    )

    st.title("🔍 Column Level Lineage Explorer")
    st.markdown("Trace column transformations across procedures, tables, and views.")


    # -------------------------------------------------
    # CACHE DATABASE CONNECTION
    # -------------------------------------------------
    @st.cache_resource
    def get_cached_connection():
        return get_connection()


    # -------------------------------------------------
    # INPUT FORM
    # -------------------------------------------------
    with st.form("lineage_form"):

        table_input = st.text_input(
            "Enter ODS Table Name (Example: ODS.SALES)"
        )

        column_input = st.text_input(
            "Enter Column Name (Example: SALE_ID)"
        )

        submitted = st.form_submit_button("Generate Lineage")


    # -------------------------------------------------
    # PROCESS
    # -------------------------------------------------
    if submitted:

        table_input = table_input.strip().upper()
        column_input = column_input.strip().upper()

        if table_input == "" or column_input == "":
            st.warning("Please enter both table and column name.")
            st.stop()

        if "." not in table_input:
            st.error("Please use format: SCHEMA.TABLE")
            st.stop()

        schema, table = table_input.split(".", 1)

        try:
            with st.spinner("Generating lineage..."):

                conn = get_cached_connection()

                result_df = get_full_column_lineage(
                    conn,
                    schema,
                    table,
                    column_input
                )

            if result_df.empty:
                st.warning("No column lineage found.")
                st.stop()

            st.success("Lineage found ✅")

            # -------------------------------------------------
            # ADD SERIAL NUMBER
            # -------------------------------------------------
            result_df = result_df.drop_duplicates()
            result_df.insert(0, "S.No", range(1, len(result_df) + 1))

            # -------------------------------------------------
            # DASHBOARD METRICS
            # -------------------------------------------------
            col1, col2, col3 = st.columns(3)

            col1.metric("Total Objects Impacted", len(result_df))
            col2.metric(
                "Tables",
                len(result_df[result_df["Object_Type"] == "TABLE"])
            )
            col3.metric(
                "Procedures",
                len(result_df[result_df["Object_Type"] == "SQL_STORED_PROCEDURE"])
            )

            st.markdown("---")

            # -------------------------------------------------
            # LINEAGE FLOW DIAGRAM
            # -------------------------------------------------
            st.subheader("📊 Lineage Flow")

            dot = Digraph()

            # Source Node
            dot.node(
                f"{schema}.{table}",
                f"{schema}.{table}\n({column_input})",
                shape="box",
                style="filled",
                fillcolor="#4CAF50"
            )

            for _, row in result_df.iterrows():

                obj_name = row["Object_Name"]
                obj_type = row["Object_Type"]
                transformation = row["Transformation"]

                # Color based on object type
                if obj_type == "VIEW":
                    color = "#2E86C1"
                elif obj_type == "TABLE":
                    color = "#17A589"
                else:
                    color = "#E67E22"

                dot.node(
                    obj_name,
                    f"{obj_name}\n[{obj_type}]",
                    shape="box",
                    style="filled",
                    fillcolor=color
                )

                dot.edge(
                    f"{schema}.{table}",
                    obj_name,
                    label=transformation
                )

            st.graphviz_chart(dot)

            st.markdown("---")

            # -------------------------------------------------
            # STYLED TABLE DISPLAY
            # -------------------------------------------------
            st.subheader("📋 Detailed Lineage Table")

            styled_df = result_df.style \
                .set_properties(**{
                    'background-color': '#F9F9F9',
                    'border-color': '#DDD'
                })

            st.dataframe(styled_df, use_container_width=True)

        except Exception as e:
            st.error(f"Error occurred: {str(e)}")