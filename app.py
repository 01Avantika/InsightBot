"""
app.py — InsightBot entry point — redirects to home page
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from db.database import init_db
init_db()

st.set_page_config(
    page_title="InsightBot — AI Data Analytics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Always go to home landing page first
st.switch_page("pages/home.py")