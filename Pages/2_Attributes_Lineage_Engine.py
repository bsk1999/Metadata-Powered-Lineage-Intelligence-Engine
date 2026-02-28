import streamlit as st
import attribute_app

st.set_page_config(
    layout="wide",
    initial_sidebar_state="collapsed"
)

attribute_app.run()