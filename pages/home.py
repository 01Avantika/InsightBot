import streamlit as st
import os
import base64

st.set_page_config(layout="wide")

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

query_params = st.query_params

if query_params.get("pages") == "analysis":
    st.switch_page("pages/analysis.py")


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
/* ===== HERO SECTION ===== */
.hero {
    background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
    padding: 4rem 6rem;
    display: flex;
    align-items: center;       
}

.hero-title {
    font-size: 50px;
    font-weight: 900;
    line-height: 1.4;
    color: #0f172a;
}

.hero-subtitle {
    font-size: 18px;
    color: #475569;
    margin-top: 1rem;
    max-width: 520px;
}

/* Buttons */
.hero-btn-primary button[kind="primary"]  {
    background-color: #16a34a !important;
    color: white !important;
    padding: 0.7rem 1.8rem;
    font-size: 16px;
    font-weight: 600;
    border-radius: 10px;
    border: none;
}


.hero-btn-primary button[kind="primary"]:hover {
    background-color: #15803d !important;
}


.hero-btn-secondary button {
    background-color: white;
    color: #334155;
    padding: 0.7rem 1.8rem;
    font-size: 16px;
    font-weight: 600;
    border-radius: 10px;
    border: 1px solid #cbd5e1;
}

.hero-btn-secondary button:hover {
    background-color: #f1f5f9;
}

div[data-testid="stHorizontalBlock"] {
    align-items: center;
}         

/* Image */
.hero-img img{
    width: 100%;
    max-width: 740px;
    height: auto;
    margin-top: -40px;
}
.upload-img img{
     width: 100%;
    max-width: 740px;
    height: auto;        
}

.card {
    display: flex;
    align-items: center;
}

/* ===== SECTION 2 ===== */
.section-two {
    width: 100%;
    padding: 80px 6%;
    background-color: #ffffff;
}

.section-grid {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 60px;
}

.section-img {
    width: 48%;
}

.section-img img {
    width: 100%;
    height: auto;
    border-radius: 14px;
    cursor: pointer;
}

.section-text {
    width: 48%;
}

.section-text h2 {
    font-size: 36px;
    font-weight: 700;
    margin-bottom: 12px;
}

.section-text p {
    font-size: 18px;
    color: #6b7280;
    line-height: 1.6;
}


</style>
""", unsafe_allow_html=True)


# ---------- HERO SECTION ----------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
hero_image = os.path.join(BASE_DIR, "assets", "image1.png")

st.markdown('<div class="hero">', unsafe_allow_html=True)

col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("""
    <div class="hero-title">
        AI-Powered Data &<br>
        Document Analysis
    </div>
    <div class="hero-subtitle">
        Upload your CSV, Excel, and PDF files, ask questions in natural language,
        and get insightful answers and reports.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    btn1, btn2 = st.columns(2)

    with btn1:
        st.markdown('<div class="hero-btn-primary">', unsafe_allow_html=True)
        if st.button("Get Started", type="primary"):
            st.switch_page("pages/analysis.py")
        st.markdown('</div>', unsafe_allow_html=True)

    with btn2:
        st.markdown('<div class="hero-btn-secondary">', unsafe_allow_html=True)
        st.button("Learn More")
        st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="hero-img">', unsafe_allow_html=True)
    st.image(hero_image)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)


# =================================================
# 🔹 SECTION 2 — UPLOAD + ASK
# =================================================
# upload_img = os.path.join(BASE_DIR, "assets", "image2.png",)
# ask_img = os.path.join(BASE_DIR, "assets", "image3.png",)
upload_img = img_to_base64("assets/image2.png")
ask_img = img_to_base64("assets/image3.png")

st.markdown(f"""
<div class="section-two">
<div class="section-grid">
<!-- LEFT IMAGE (Upload) -->
<div class="section-img"> <a href="/analysis" target="_self"><img src='data:image/png;base64,{upload_img}'></a>
</div>
<!-- RIGHT IMAGE (AI UI) -->
<div class="section-img"> <img src='data:image/png;base64,{ask_img}'>
</div>
</div>
</div>
""", unsafe_allow_html=True)

# =================================================
# 🔹 SECTION 3 — INSIGHTS & CTA
# =================================================
# footer_img = os.path.join(BASE_DIR, "assets", "image4.png",)
# st.image(footer_image)
st.markdown("""
<style>
.section {
    padding-top: 20px;
    padding-bottom: 10px;
}

/* Card styling applied to column */
[data-testid="column"] > div {
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 18px;
    background: white;
    text-align: center;
}

/* Image tuning */
[data-testid="column"] img {
    max-height: 150px;
    display: block;
    margin: auto;
}

/* Center text */
.center-text {
    text-align: center;
}

/* Center button perfectly */
.center-btn {
    display: flex;
    justify-content: center;
    margin-top: 16px;
}

/* Button styling */
.stButton > button {
    background-color: #15803d !important;
    color: white !important;
    border-radius: 14px;
    padding: 14px 48px;
    font-size: 18px;
    border: none;
}

.stButton > button:hover {
    background-color: #16a34a !important;
}
</style>
""", unsafe_allow_html=True)

# -------- SECTION --------
st.markdown("<div class='section'>", unsafe_allow_html=True)

st.markdown("<h2 class='center-text'>Get Instant Insights & Reports</h2>", unsafe_allow_html=True)

st.markdown(
    "<p class='center-text' style='margin-bottom:30px;'>"
    "Receive summarized insights and executive-level reports generated by our AI, "
    "including trend detection, data visualization, and intelligent answers to your questions."
    "</p>",
    unsafe_allow_html=True
)

# -------- CARDS --------
c1, c2, c3 = st.columns(3)

with c1:
    st.image("assets/image4.png")
    st.markdown("### Charts & Graphs")
    st.caption("Auto-generated visuals for quick understanding")

with c2:
    st.image("assets/image5.png")
    st.markdown("### Trend Analysis")
    st.caption("Identify patterns, growth, and anomalies")

with c3:
    st.image("assets/image6.png")
    st.markdown("### Summary Reports")
    st.caption("Executive-ready AI generated reports")

# -------- CTA --------
st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    "<h4 class='center-text'>Start Uploading Your Files and Ask Questions Instantly!</h4>",
    unsafe_allow_html=True
)

left, center, right = st.columns([1, 0.5, 1])

with center:
    if st.button("Get Started"):
        st.switch_page("pages/analysis.py")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# ------------------ Footer ------------------
st.markdown("---")
st.markdown("Built with using **Streamlit + LLMs**")
