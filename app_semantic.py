import streamlit as st
import networkx as nx
import pandas as pd
from lineage_builder import build_lineage
from graphviz import Digraph


def run():

    # --------------------------------------------------
    # MODULE TITLE (NOT PAGE TITLE)
    # --------------------------------------------------

    st.markdown("## 📊 Semantic Model – Full Impact Lineage Explorer")

    # --------------------------------------------------
    # BUILD LINEAGE (CACHED)
    # --------------------------------------------------

    @st.cache_data(show_spinner=True)
    def load_lineage():
        return build_lineage()

    df_lineage, G = load_lineage()

    if G.number_of_nodes() == 0:
        st.warning("No lineage data found.")
        return

    all_nodes = sorted(G.nodes)

    selected_node = st.selectbox(
        "🎯 Select Column / Measure / Table",
        all_nodes
    )

    # --------------------------------------------------
    # FULL IMPACT SUBGRAPH
    # --------------------------------------------------

    upstream = nx.ancestors(G, selected_node)
    downstream = nx.descendants(G, selected_node)

    impact_nodes = set(upstream) | set(downstream) | {selected_node}
    subgraph = G.subgraph(impact_nodes)

    # --------------------------------------------------
    # LEVEL COMPUTATION (For Table View)
    # --------------------------------------------------

    def build_flow_table(graph, selected):

        flow_rows = []

        upstream_levels = {}
        queue = [(selected, 0)]
        visited = set()

        while queue:
            node, level = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            upstream_levels[node] = level

            for predecessor in graph.predecessors(node):
                queue.append((predecessor, level - 1))

        downstream_levels = {}
        queue = [(selected, 0)]
        visited = set()

        while queue:
            node, level = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            downstream_levels[node] = level

            for successor in graph.successors(node):
                queue.append((successor, level + 1))

        for source, target, data in graph.edges(data=True):

            if source in upstream_levels:
                level = upstream_levels[source]
            elif source in downstream_levels:
                level = downstream_levels[source]
            else:
                level = 0

            flow_rows.append({
                "Level": level,
                "Source": source,
                "Target": target,
                "DependencyType": data.get("dependency", ""),
                "Transformation": data.get("transformation", "")
            })

        df_flow = pd.DataFrame(flow_rows)
        df_flow = df_flow.sort_values(["Level", "Source"])

        return df_flow

    df_flow = build_flow_table(subgraph, selected_node)

    # --------------------------------------------------
    # KPI SUMMARY
    # --------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("🔼 Upstream Nodes", len(upstream))
    col2.metric("🔽 Downstream Nodes", len(downstream))
    col3.metric("📊 Total Impact", len(impact_nodes))
    col4.metric("🔗 Total Dependencies", len(df_flow))

    st.markdown("---")

    # --------------------------------------------------
    # VIEW TOGGLE
    # --------------------------------------------------

    view_option = st.radio(
        "Select View",
        ["📋 Tabular Flow View", "🌳 Tree Graph View"],
        horizontal=True
    )

    # --------------------------------------------------
    # TABULAR VIEW
    # --------------------------------------------------

    if view_option == "📋 Tabular Flow View":

        st.markdown("### 📋 Detailed Lineage Table")
        st.dataframe(df_flow, use_container_width=True)

        csv = df_flow.to_csv(index=False).encode("utf-8")

        st.download_button(
            "⬇ Download Lineage CSV",
            csv,
            "lineage_flow.csv",
            "text/csv"
        )

    # --------------------------------------------------
    # TREE GRAPH VIEW
    # --------------------------------------------------

    else:

        st.markdown("### 🌳 Enterprise Lineage Tree (Interactive)")

        dot = Digraph(format="svg")
        dot.attr(rankdir="LR")
        dot.attr(bgcolor="white")
        dot.attr(ranksep="1.8")
        dot.attr(nodesep="1.2")

        dot.attr(
            "node",
            shape="box",
            style="filled,rounded",
            fontname="Arial",
            fontsize="16",
            penwidth="1.5"
        )

        dot.attr(
            "edge",
            fontname="Arial",
            fontsize="11",
            arrowsize="0.8"
        )

        color_map = {
            "Column Reference": "#1976D2",
            "Measure Reference": "#F57C00",
            "RELATED Relationship": "#D32F2F",
            "Model Relationship": "#7B1FA2",
            "Source Mapping": "#388E3C"
        }

        for node in subgraph.nodes:
            if node == selected_node:
                dot.node(node, label=node, fillcolor="#000000", fontcolor="white")
            else:
                dot.node(node, label=node, fillcolor="#E3F2FD", fontcolor="black")

        for source, target, data in subgraph.edges(data=True):

            dep_type = data.get("dependency", "")
            transformation = data.get("transformation", "")
            edge_color = color_map.get(dep_type, "#90A4AE")

            label_text = dep_type
            if transformation:
                label_text += "\\n" + transformation[:60]

            dot.edge(source, target, label=label_text, color=edge_color)

        svg = dot.pipe().decode("utf-8")

        interactive_html = f"""
        <div style="margin-bottom:10px;">
            <button onclick="zoomIn()">➕ Zoom</button>
            <button onclick="zoomOut()">➖ Zoom</button>
            <button onclick="resetZoom()">🔄 Reset</button>
        </div>

        <div id="wrapper" style="
            width:100%;
            height:800px;
            overflow:auto;
            background:white;
            border:1px solid #ddd;
            border-radius:12px;
        ">
            <div id="zoom-container">
                {svg}
            </div>
        </div>

        <script>
        (function() {{
            let scale = 1;
            const container = document.getElementById("zoom-container");

            window.zoomIn = function() {{
                scale += 0.1;
                container.style.transform = "scale(" + scale + ")";
            }}

            window.zoomOut = function() {{
                scale -= 0.1;
                if (scale < 0.3) scale = 0.3;
                container.style.transform = "scale(" + scale + ")";
            }}

            window.resetZoom = function() {{
                scale = 1;
                container.style.transform = "scale(1)";
            }}
        }})();
        </script>
        """

        st.components.v1.html(interactive_html, height=900)

    # --------------------------------------------------
    # MODULE FOOTER
    # --------------------------------------------------

    st.markdown(
        "<hr><center style='color:gray'>Semantic Lineage Module</center>",
        unsafe_allow_html=True
    )