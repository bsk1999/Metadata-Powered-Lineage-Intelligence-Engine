import streamlit as st
import app_semantic

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)


app_semantic.run()
