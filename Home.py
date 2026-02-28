import streamlit as st
import os

st.set_page_config(
    page_title="Enterprise Data Lineage Platform",
    page_icon="🔗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -------------------------
# DARK ENTERPRISE GLASS UI
# -------------------------
st.markdown("""
<style>

/* Background */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a, #111827);
    color: white;
}

/* Proper top spacing */
.block-container {
    padding-top: 2.5rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

/* Enterprise Header Bar */
.enterprise-header {
    background: rgba(255,255,255,0.05);
    padding: 25px 40px;
    border-radius: 14px;
    margin-bottom: 50px;
    border: 1px solid rgba(255,255,255,0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header-title {
    font-size: 22px;
    font-weight: 600;
}

.header-meta {
    font-size: 14px;
    color: #cbd5e1;
}

/* Main Title */
.main-title {
    font-size: 52px;
    font-weight: 800;
    background: linear-gradient(90deg,#00F5A0,#00D9F5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

/* Subtitle */
.subtitle {
    font-size: 20px;
    color: #cbd5e1;
    margin-bottom: 40px;
}

/* Section Title */
.section-title {
    font-size: 26px;
    font-weight: 600;
    margin-top: 80px;
    margin-bottom: 25px;
}

/* Glass Cards */
.glass-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 30px;
    transition: all 0.3s ease;
    border: 1px solid rgba(255,255,255,0.1);
    min-height: 260px;
}

.glass-card:hover {
    transform: translateY(-12px);
    box-shadow: 0px 20px 50px rgba(0,0,0,0.6);
}

/* Team container */
.team-container {
    margin-top: 20px;
}

/* Footer */
.footer {
    text-align:center;
    color:#94a3b8;
    margin-top:100px;
    padding:30px;
    font-size:14px;
    border-top: 1px solid rgba(255,255,255,0.08);
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# ENTERPRISE HEADER BAR
# -------------------------
st.markdown("""
<div class="enterprise-header">
    <div class="header-title">🔗 Enterprise Data Lineage Platform</div>
    <div class="header-meta">Version 1.0 • Built by Shyam Kumar Boodidi</div>
</div>
""", unsafe_allow_html=True)

# -------------------------
# HERO SECTION
# -------------------------
st.markdown('<div class="main-title">Enterprise Data Lineage Platform</div>', unsafe_allow_html=True)

st.markdown("""
<div class="subtitle">
Trace dependencies across Power BI, SQL Server, and Azure Synapse.<br>
Visualize transformations. Analyze impact. Govern your data with confidence.
</div>
""", unsafe_allow_html=True)

# -------------------------
# PLATFORM STATS
# -------------------------
col1, col2, col3 = st.columns(3)
col1.metric("Column Dependencies Tracked", "5000+")
col2.metric("SQL Objects Parsed", "350+")
col3.metric("Semantic Objects Indexed", "120+")

st.markdown("---")

# -------------------------
# FEATURE CARDS
# -------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="glass-card">
        <h3>🏗 Procedure & View Lineage Explorer</h3>
        MERGE + INSERT transformation tracking in Azure Synapse.
        <br><br>
        👉 Open from sidebar
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="glass-card">
        <h3>🔍 Attribute-Level Lineage Tracker</h3>
        SQL AST-based parsing for procedures & views.
        <br><br>
        👉 Open from sidebar
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="glass-card">
        <h3>📊 PBI Semantic Columnar Lineage</h3>
        Full upstream & downstream impact analysis using XMLA metadata.
        <br><br>
        👉 Open from sidebar
    </div>
    """, unsafe_allow_html=True)

# -------------------------
# ARCHITECTURE SECTION
# -------------------------
st.markdown('<div class="section-title">🧠 Platform Architecture</div>', unsafe_allow_html=True)

st.code("""
User Interface (Streamlit)
        │
        ├── Semantic Engine (XMLA + DAX Parser + NetworkX)
        ├── SQL AST Engine (sqlglot)
        └── Synapse Engine (pyodbc + ODBC 18)
""")

# ---------------------------------------------------
# TEAM SECTION
# ---------------------------------------------------
st.markdown('<div class="section-title">Our Team</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 1.8], gap="large")

image_path = os.path.join(os.path.dirname(__file__), "team_photo.png")

with col1:
    st.image(image_path, use_container_width=True)

with col2:
    st.markdown("""
        <h2 style="margin-bottom:15px;">Team Name: Elite Techies 🚀</h2>

        <p style="font-size:17px; line-height:1.6; color:#cbd5e1;">
        We are a team of data engineers focused on building enterprise-grade 
        metadata intelligence and lineage solutions.
        </p>

        <p style="font-size:17px; line-height:1.6; color:#cbd5e1;">
        This platform was designed to improve visibility, governance, 
        and transformation transparency across BI and Data Warehouse systems.
        </p>
    """, unsafe_allow_html=True)

# -------------------------
# FOOTER
# -------------------------
st.markdown("""
<div class="footer">
Enterprise Lineage Platform • Internal Data Governance Tool • © 2026
</div>
""", unsafe_allow_html=True)