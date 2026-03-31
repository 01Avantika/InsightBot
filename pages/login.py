"""
pages/login.py — Authentication page for InsightBot
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from db.database import create_user, verify_user, init_db

init_db()

st.set_page_config(page_title="InsightBot — Login", page_icon="🤖", layout="centered")

if st.session_state.get("user"):
    st.switch_page("pages/dashboard.py")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }
    .brand { text-align: center; margin-bottom: 1.5rem; }
    .brand h1 { color: #a78bfa; font-size: 2.5rem; margin: 0; }
    .brand p  { color: #94a3b8; font-size: 0.95rem; }
    div[data-testid="stTextInput"] input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(167,139,250,0.3) !important;
        color: #f1f5f9 !important;
        border-radius: 10px !important;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #7c3aed, #a78bfa) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; width: 100% !important;
        padding: 0.6rem !important; font-size: 1rem !important;
        font-weight: 600 !important;
    }
    .stTabs [data-baseweb="tab"] { color: #94a3b8 !important; }
    .stTabs [aria-selected="true"] { color: #a78bfa !important; border-bottom-color: #a78bfa !important; }
    label { color: #cbd5e1 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brand">
    <h1>🤖 InsightBot</h1>
    <p>AI-Powered Data Analysis & Document Intelligence</p>
</div>
""", unsafe_allow_html=True)

tab_login, tab_signup = st.tabs(["🔑 Login", "✨ Create Account"])

with tab_login:
    st.subheader("Welcome back")
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="your_username")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submit   = st.form_submit_button("Sign In")

    if submit:
        if not username or not password:
            st.error("Please fill in all fields.")
        else:
            user = verify_user(username, password)
            if user:
                st.session_state["user"] = user
                st.session_state["chat_history"] = []
                st.success(f"Welcome back, **{user['username']}**! 🎉")
                st.switch_page("pages/dashboard.py")
            else:
                st.error("Invalid username or password.")

with tab_signup:
    st.subheader("Create your account")
    with st.form("signup_form"):
        new_username = st.text_input("Username", placeholder="choose_a_username")
        new_email    = st.text_input("Email",    placeholder="you@example.com")
        new_password = st.text_input("Password", type="password", placeholder="Min. 8 characters")
        confirm_pwd  = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
        signup_btn   = st.form_submit_button("Create Account")

    if signup_btn:
        if not all([new_username, new_email, new_password, confirm_pwd]):
            st.error("Please fill in all fields.")
        elif len(new_password) < 8:
            st.error("Password must be at least 8 characters.")
        elif new_password != confirm_pwd:
            st.error("Passwords do not match.")
        else:
            try:
                user = create_user(new_username, new_email, new_password)
                st.session_state["user"] = {"id": user["id"], "username": user["username"], "email": user["email"]}
                st.session_state["chat_history"] = []
                st.success("Account created! Redirecting…")
                st.switch_page("pages/dashboard.py")
            except ValueError as e:
                st.error(str(e))
