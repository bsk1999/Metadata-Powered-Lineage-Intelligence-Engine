import streamlit as st
import pandas as pd
from graphviz import Digraph

from db_connection import get_connection
from lineage_service import get_full_column_lineage


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
        "Enter Table Name (Example: ODS.SALES)"
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
        # CLEAN & SERIAL NUMBER
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
        # LINEAGE FLOW DIAGRAM (TRUE HIERARCHY)
        # -------------------------------------------------
        st.subheader("📊 End-to-End Lineage Flow")

        dot = Digraph(engine="dot")
        dot.attr(rankdir="LR")
        dot.attr(nodesep="0.8")
        dot.attr(ranksep="1")

        source_node = f"{schema}.{table}"

        # Source Node
        dot.node(
            source_node,
            f"{source_node}\n({column_input})",
            shape="box",
            style="filled",
            fillcolor="#4CAF50"
        )

        added_nodes = set([source_node])
        added_edges = set()

        procedures = result_df[
            result_df["Object_Type"] == "SQL_STORED_PROCEDURE"
        ]["Object_Name"].unique()

        tables = result_df[
            result_df["Object_Type"] == "TABLE"
        ]["Object_Name"].unique()

        views = result_df[
            result_df["Object_Type"] == "VIEW"
        ]["Object_Name"].unique()

        # -----------------------------
        # ADD PROCEDURES
        # -----------------------------
        for proc in procedures:

            if proc not in added_nodes:
                dot.node(
                    proc,
                    f"{proc}\n[PROCEDURE]",
                    shape="box",
                    style="filled",
                    fillcolor="#E67E22"
                )
                added_nodes.add(proc)

            edge = (source_node, proc)
            if edge not in added_edges:
                dot.edge(source_node, proc)
                added_edges.add(edge)

        # -----------------------------
        # ADD TABLES
        # -----------------------------
        for tbl in tables:

            if tbl not in added_nodes:
                dot.node(
                    tbl,
                    f"{tbl}\n[TABLE]",
                    shape="box",
                    style="filled",
                    fillcolor="#17A589"
                )
                added_nodes.add(tbl)

            connected = False

            for proc in procedures:
                edge = (proc, tbl)
                if edge not in added_edges:
                    dot.edge(proc, tbl)
                    added_edges.add(edge)
                    connected = True

            if not connected:
                edge = (source_node, tbl)
                if edge not in added_edges:
                    dot.edge(source_node, tbl)
                    added_edges.add(edge)

        # -----------------------------
        # ADD VIEWS
        # -----------------------------
        for vw in views:

            if vw not in added_nodes:
                dot.node(
                    vw,
                    f"{vw}\n[VIEW]",
                    shape="box",
                    style="filled",
                    fillcolor="#2E86C1"
                )
                added_nodes.add(vw)

            connected = False

            for tbl in tables:
                edge = (tbl, vw)
                if edge not in added_edges:
                    dot.edge(tbl, vw)
                    added_edges.add(edge)
                    connected = True

            if not connected:
                edge = (source_node, vw)
                if edge not in added_edges:
                    dot.edge(source_node, vw)
                    added_edges.add(edge)

        st.graphviz_chart(dot)

        st.markdown("---")

        # -------------------------------------------------
        # STYLED TABLE DISPLAY
        # -------------------------------------------------
        st.subheader("📋 Detailed Lineage Table")

        styled_df = result_df.style.set_properties(**{
            'background-color': '#F9F9F9',
            'border-color': '#DDD'
        })

        st.dataframe(styled_df, use_container_width=True)

    except Exception as e:
        st.error(f"Error occurred: {str(e)}")
