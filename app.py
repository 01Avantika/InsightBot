import streamlit as st

st.set_page_config(layout="wide")

st.markdown("""
<style>
/* Hide sidebar completely */
section[data-testid="stSidebar"] {
    display: none;
}

/* Remove left padding caused by sidebar */
div[data-testid="stAppViewContainer"] {
    padding-left: 0;
}
</style>
""", unsafe_allow_html=True)


# Redirect immediately to home page
st.switch_page("pages/home.py")
