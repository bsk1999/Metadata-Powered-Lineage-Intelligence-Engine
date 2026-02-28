import streamlit as st
import vw_proc_app

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

vw_proc_app.run()