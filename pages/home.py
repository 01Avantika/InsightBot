"""
pages/home.py — InsightBot Landing Page
"""
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(
    page_title="InsightBot — AI Data Analytics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

is_dark = st.session_state["theme"] == "dark"

if is_dark:
    bg="08090f"; bg2="0e1117"; bg3="0b0d16"
    text="f0f2f8"; text2="8892a4"; text3="3d4455"
    card_bg="rgba(255,255,255,0.03)"; card_bg2="rgba(255,255,255,0.055)"
    card_border="rgba(120,80,255,0.16)"; card_border2="rgba(120,80,255,0.35)"
    nav_bg="rgba(8,9,15,0.94)"; footer_bg="06070d"
    pill_bg="rgba(120,80,255,0.1)"; pill_border="rgba(120,80,255,0.28)"
    stat_bg="0e1117"; tog_bg="rgba(255,255,255,0.07)"; tog_border="rgba(255,255,255,0.15)"
    tog_color="c4b5fd"; btn_sh="rgba(109,40,217,0.45)"
else:
    bg="fafbff"; bg2="ffffff"; bg3="f4f5ff"
    text="0d0f1a"; text2="5a6478"; text3="aab4c4"
    card_bg="rgba(255,255,255,0.92)"; card_bg2="rgba(248,249,255,0.98)"
    card_border="rgba(109,40,217,0.1)"; card_border2="rgba(109,40,217,0.3)"
    nav_bg="rgba(250,251,255,0.94)"; footer_bg="f1f2ff"
    pill_bg="rgba(109,40,217,0.07)"; pill_border="rgba(109,40,217,0.2)"
    stat_bg="ffffff"; tog_bg="rgba(0,0,0,0.05)"; tog_border="rgba(0,0,0,0.12)"
    tog_color="6d28d9"; btn_sh="rgba(109,40,217,0.3)"

tl = "Light Mode" if is_dark else "Dark Mode"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*,*::before,*::after{{box-sizing:border-box;font-family:'Inter',sans-serif!important;}}
html,body,.stApp{{background:#{bg}!important;color:#{text}!important;margin:0;padding:0;}}
#MainMenu,footer,header{{visibility:hidden!important;}}
[data-testid="stSidebar"],[data-testid="collapsedControl"]{{display:none!important;}}
.block-container{{padding:0!important;max-width:100%!important;}}
section[data-testid="stMain"]>div{{padding:0!important;}}
div[data-testid="stVerticalBlock"]>div{{padding:0!important;gap:0!important;}}

@keyframes fadeUp{{from{{opacity:0;transform:translateY(20px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes shimmer{{0%{{background-position:-400% center}}100%{{background-position:400% center}}}}
@keyframes pulseDot{{0%,100%{{opacity:1}}50%{{opacity:0.4}}}}
@keyframes gradMove{{0%{{background-position:0% 50%}}50%{{background-position:100% 50%}}100%{{background-position:0% 50%}}}}

.navbar{{
  position:fixed;top:0;left:0;right:0;z-index:9999;
  background:{nav_bg};backdrop-filter:blur(24px);
  border-bottom:1px solid #{card_border.replace('rgba(120,80,255,0.16)','1a1a2e') if is_dark else '1a1a2e'};
  padding:0 3rem;height:58px;
  display:flex;align-items:center;justify-content:space-between;
  border-bottom:1px solid rgba(255,255,255,{'.06' if is_dark else '.12'});
}}
.nav-brand{{font-size:1.1rem;font-weight:800;letter-spacing:-0.5px;
  background:linear-gradient(135deg,#8b5cf6,#a78bfa);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.nav-mid{{display:flex;gap:2rem;align-items:center;}}
.nav-link{{color:#{text2};text-decoration:none;font-size:0.75rem;font-weight:600;
  letter-spacing:0.1em;text-transform:uppercase;transition:color 0.2s;}}
.nav-link:hover{{color:#{text};}}
.nav-right{{display:flex;align-items:center;}}
.tog{{
  background:{tog_bg};border:1px solid {tog_border};
  color:#{tog_color};border-radius:6px;
  padding:0.3rem 0.75rem;font-size:0.7rem;font-weight:700;
  letter-spacing:0.08em;text-transform:uppercase;cursor:pointer;
  white-space:nowrap;line-height:1.4;
}}

.hero{{
  min-height:100vh;background:#{bg};
  background-image:
    radial-gradient(ellipse 75% 55% at 50% -8%,rgba(109,40,217,0.24) 0%,transparent 65%),
    radial-gradient(ellipse 30% 28% at 88% 65%,rgba(59,130,246,0.07) 0%,transparent 55%);
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  text-align:center;padding:6rem 2rem 2rem;
}}
.badge{{
  display:inline-flex;align-items:center;gap:0.5rem;
  background:{pill_bg};border:1px solid {pill_border};
  border-radius:4px;padding:0.32rem 0.9rem;
  font-size:0.65rem;font-weight:700;color:#a78bfa;
  letter-spacing:0.14em;text-transform:uppercase;margin-bottom:1.8rem;
  animation:fadeUp 0.5s ease both;
}}
.dot{{width:5px;height:5px;border-radius:50%;background:#a78bfa;animation:pulseDot 2s ease-in-out infinite;}}
.h1{{
  font-size:clamp(2.8rem,5vw,4.8rem);font-weight:900;line-height:1.06;
  letter-spacing:-2.5px;color:#{text};margin:0 0 1.3rem;max-width:760px;
  animation:fadeUp 0.6s ease 0.1s both;
}}
.h1 .g{{
  background:linear-gradient(135deg,#7c3aed 0%,#a78bfa 45%,#818cf8 100%);
  background-size:300% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;
  animation:shimmer 4s linear infinite;
}}
.sub{{
  font-size:1rem;color:#{text2};max-width:500px;line-height:1.8;
  margin:0 auto 0.5rem;animation:fadeUp 0.6s ease 0.2s both;
}}

.stats{{
  background:#{stat_bg};
  border-top:1px solid rgba(255,255,255,{'.05' if is_dark else '.0'});
  border-bottom:1px solid rgba(255,255,255,{'.05' if is_dark else '.0'});
  {'border-top:1px solid rgba(0,0,0,.06);border-bottom:1px solid rgba(0,0,0,.06);' if not is_dark else ''}
  display:grid;grid-template-columns:repeat(4,1fr);padding:2.2rem 4rem;gap:1rem;
}}
.sn{{font-size:2.1rem;font-weight:900;letter-spacing:-1px;
  background:linear-gradient(135deg,#7c3aed,#a78bfa);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.sl{{font-size:0.72rem;color:#{text3};font-weight:600;letter-spacing:0.06em;margin-top:0.2rem;text-transform:uppercase;}}

.sec{{padding:6rem 5rem;background:#{bg3};}}
.sec-alt{{padding:6rem 5rem;background:#{bg2};}}
.ey{{text-align:center;font-size:0.65rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:#8b5cf6;margin-bottom:0.7rem;}}
.sh2{{text-align:center;font-size:clamp(1.6rem,2.6vw,2.2rem);font-weight:800;color:#{text};letter-spacing:-0.6px;margin:0 0 0.7rem;}}
.ssub{{text-align:center;color:#{text2};font-size:0.87rem;max-width:480px;margin:0 auto 3.5rem;line-height:1.75;}}

.grid{{
  display:grid;grid-template-columns:repeat(3,1fr);
  gap:1px;background:rgba(255,255,255,{'.06' if is_dark else '.0'});
  {'border:1px solid rgba(0,0,0,.07);' if not is_dark else 'border:1px solid rgba(255,255,255,.06);'}
  border-radius:18px;overflow:hidden;max-width:1060px;margin:0 auto;
}}
.cell{{
  background:{card_bg};padding:2rem 1.8rem;
  transition:background 0.3s;position:relative;
}}
.cell:hover{{background:{card_bg2};}}
.cell::after{{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(139,92,246,0.5),transparent);
  opacity:0;transition:opacity 0.3s;
}}
.cell:hover::after{{opacity:1;}}
.cnum{{font-size:0.6rem;font-weight:800;letter-spacing:0.14em;color:#{text3};text-transform:uppercase;margin-bottom:1rem;font-variant-numeric:tabular-nums;}}
.ctitle{{font-size:0.9rem;font-weight:700;color:#{text};margin-bottom:0.55rem;letter-spacing:-0.1px;}}
.cdesc{{font-size:0.8rem;color:#{text2};line-height:1.7;}}

.steps{{display:grid;grid-template-columns:repeat(4,1fr);gap:1.2rem;max-width:920px;margin:0 auto;}}
.step{{
  background:{card_bg};border:1px solid rgba(255,255,255,{'.06' if is_dark else '0'});
  {'border:1px solid rgba(0,0,0,.07);' if not is_dark else ''}
  border-radius:14px;padding:1.8rem 1.4rem;text-align:center;transition:all 0.3s;
}}
.step:hover{{transform:translateY(-4px);border-color:rgba(139,92,246,0.35);}}
.snum{{
  width:40px;height:40px;border-radius:10px;
  background:linear-gradient(135deg,#5b21b6,#7c3aed);
  color:white;font-size:0.85rem;font-weight:800;
  display:flex;align-items:center;justify-content:center;margin:0 auto 1.1rem;
}}
.st{{font-size:0.85rem;font-weight:700;color:#{text};margin-bottom:0.45rem;}}
.sd{{font-size:0.77rem;color:#{text2};line-height:1.65;}}

.stack-wrap{{max-width:900px;margin:0 auto;}}
.stack-row{{display:flex;gap:3rem;align-items:flex-start;flex-wrap:wrap;margin-bottom:2rem;}}
.stack-group{{flex:1;min-width:180px;}}
.sg-label{{font-size:0.62rem;font-weight:800;letter-spacing:0.15em;text-transform:uppercase;color:#8b5cf6;margin-bottom:0.8rem;}}
.sg-text{{font-size:0.88rem;font-weight:500;color:#{text2};line-height:1.8;}}

.cta{{
  background:linear-gradient(135deg,#2e1065 0%,#4c1d95 40%,#1e1b4b 100%);
  background-size:300% 300%;animation:gradMove 8s ease infinite;
  padding:6rem 3rem;text-align:center;position:relative;overflow:hidden;
}}
.cta::before{{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 55% 45% at 50% 0%,rgba(255,255,255,0.07) 0%,transparent 60%);
  pointer-events:none;
}}
.cta-h{{font-size:clamp(1.8rem,3vw,2.8rem);font-weight:900;color:white;letter-spacing:-1px;margin-bottom:0.8rem;}}
.cta-p{{color:rgba(255,255,255,0.6);font-size:0.95rem;margin-bottom:2.2rem;}}

div.stButton>button{{
  background:linear-gradient(135deg,#5b21b6,#7c3aed,#8b5cf6)!important;
  background-size:200% auto!important;color:white!important;border:none!important;
  border-radius:8px!important;font-weight:700!important;font-size:0.8rem!important;
  letter-spacing:0.08em!important;text-transform:uppercase!important;
  padding:0.7rem 2rem!important;
  box-shadow:0 4px 24px {btn_sh}!important;transition:all 0.25s!important;
}}
div.stButton>button:hover{{transform:translateY(-2px)!important;box-shadow:0 8px 32px {btn_sh}!important;}}

.foot{{
  background:#{footer_bg};
  border-top:1px solid rgba(255,255,255,{'.05' if is_dark else '0'});
  {'border-top:1px solid rgba(0,0,0,.07);' if not is_dark else ''}
  padding:2rem 4rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;
}}
.fb{{font-size:0.9rem;font-weight:800;background:linear-gradient(135deg,#8b5cf6,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
.fc{{font-size:0.74rem;color:#{text3};}}
</style>
""", unsafe_allow_html=True)

# NAVBAR — pure HTML, toggle as Streamlit button in fixed position
st.markdown(f"""
<div class="navbar">
  <div class="nav-brand">InsightBot</div>
  <div class="nav-mid">
    <a class="nav-link" href="#features">Features</a>
    <a class="nav-link" href="#process">Process</a>
    <a class="nav-link" href="#stack">Stack</a>
  </div>
  <div class="nav-right" id="tog-anchor"></div>
</div>
""", unsafe_allow_html=True)

# Theme toggle — fixed position top right, small pill
st.markdown(f"""
<style>
  div[data-testid="stHorizontalBlock"] {{ gap: 0 !important; }}
  .tog-fixed {{
    position: fixed; top: 14px; right: 2.5rem; z-index: 99999;
  }}
  .tog-fixed > div > button {{
    background: {tog_bg} !important;
    border: 1px solid {tog_border} !important;
    color: #{tog_color} !important;
    border-radius: 5px !important;
    padding: 0.28rem 0.7rem !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    box-shadow: none !important;
    min-height: 0 !important;
    line-height: 1.3 !important;
  }}
  .tog-fixed > div > button:hover {{ opacity: 0.85 !important; transform: none !important; }}
</style>
<div class="tog-fixed" id="tog-wrap">
""", unsafe_allow_html=True)

if st.button(tl, key="theme_nav"):
    st.session_state["theme"] = "light" if is_dark else "dark"
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# HERO
st.markdown(f"""
<div class="hero">
  <div class="badge"><span class="dot"></span>AI-Powered Data Intelligence Platform</div>
  <h1 class="h1">Turn Your Data Into<br><span class="g">Actionable Insights</span></h1>
  <p class="sub">Upload CSVs, Excel files, or PDFs and instantly get AI-generated analysis,
  beautiful visualizations, and conversational Q&amp;A — no coding required.</p>
</div>
""", unsafe_allow_html=True)

# GET STARTED button directly below hero
c1,c2,c3 = st.columns([3.5,1,3.5])
with c2:
    if st.button("Get Started", key="hero_cta"):
        st.switch_page("pages/login.py")

# STATS
st.markdown(f"""
<div class="stats">
  <div><div class="sn">3+</div><div class="sl">File Formats</div></div>
  <div><div class="sn">10+</div><div class="sl">Chart Types</div></div>
  <div><div class="sn">3</div><div class="sl">LLM Providers</div></div>
  <div><div class="sn">100%</div><div class="sl">No Code Required</div></div>
</div>
""", unsafe_allow_html=True)

# FEATURES
st.markdown(f"""
<div class="sec" id="features">
  <div class="ey">Platform Capabilities</div>
  <h2 class="sh2">Everything You Need</h2>
  <div class="ssub">A complete data intelligence platform — from raw file to boardroom insight.</div>
  <div class="grid">
    <div class="cell"><div class="cnum">01</div><div class="ctitle">Secure Authentication</div><div class="cdesc">Full login and signup with bcrypt password hashing. User data is isolated, encrypted, and persistent across sessions.</div></div>
    <div class="cell"><div class="cnum">02</div><div class="ctitle">Multi-Format Upload</div><div class="cdesc">Upload CSV, Excel (.xlsx/.xls), and PDF files up to 100 MB. Resume any previous file without re-uploading.</div></div>
    <div class="cell"><div class="cnum">03</div><div class="ctitle">Automated EDA</div><div class="cdesc">Instant exploratory analysis covering shape, types, missing values, distributions, outliers, and correlations — generated automatically.</div></div>
    <div class="cell"><div class="cnum">04</div><div class="ctitle">Dynamic Visualizations</div><div class="cdesc">Six chart types via a custom builder: scatter, bar, line, histogram, box, and pie — all rendered interactively with Plotly.</div></div>
    <div class="cell"><div class="cnum">05</div><div class="ctitle">AI-Generated Insights</div><div class="cdesc">Powered by Groq, OpenAI GPT-4o, or Google Gemini. Executive-level summaries and pattern detection with one click.</div></div>
    <div class="cell"><div class="cnum">06</div><div class="ctitle">Conversational Q&amp;A</div><div class="cdesc">Ask questions in plain English. Pandas-powered direct computation with LLM fallback for complex analytical queries.</div></div>
    <div class="cell"><div class="cnum">07</div><div class="ctitle">PDF Document Q&amp;A</div><div class="cdesc">FAISS vector indexing over PDF content enables accurate, context-aware retrieval-augmented generation answers.</div></div>
    <div class="cell"><div class="cnum">08</div><div class="ctitle">AutoML Predictions</div><div class="cdesc">Automated machine learning pipeline that trains, evaluates, and explains classification and regression models on your dataset — no code needed.</div></div>
    <div class="cell"><div class="cnum">09</div><div class="ctitle">History &amp; Report Export</div><div class="cdesc">Every session persisted. Resume any past conversation and download a full structured analysis report for stakeholders.</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

# PROCESS
st.markdown(f"""
<div class="sec-alt" id="process">
  <div class="ey">Workflow</div>
  <h2 class="sh2">From Data to Decision in Four Steps</h2>
  <div class="ssub">A streamlined process designed to eliminate friction between raw data and actionable intelligence.</div>
  <div class="steps">
    <div class="step"><div class="snum">01</div><div class="st">Create Account</div><div class="sd">Sign up in seconds. Files, analyses, and conversations are securely stored per account.</div></div>
    <div class="step"><div class="snum">02</div><div class="st">Upload Your File</div><div class="sd">Drop any CSV, Excel, or PDF. Automatic format detection and parsing happens instantly.</div></div>
    <div class="step"><div class="snum">03</div><div class="st">Explore &amp; Predict</div><div class="sd">Auto-generated charts, AI insights, and AutoML predictive models appear immediately after upload.</div></div>
    <div class="step"><div class="snum">04</div><div class="st">Chat &amp; Export</div><div class="sd">Ask natural language questions and download a structured analysis report for your team.</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

# TECH STACK — described in plain language, not listed
st.markdown(f"""
<div class="sec" id="stack">
  <div class="ey">Technology</div>
  <h2 class="sh2">Built on a Modern, Scalable Foundation</h2>
  <div class="ssub">Every layer chosen for reliability, speed, and intelligence.</div>
  <div class="stack-wrap">
    <div class="stack-row">
      <div class="stack-group">
        <div class="sg-label">Interface</div>
        <div class="sg-text">A reactive web application framework delivers a fast, responsive UI with zero HTML — every interaction updates in real time without page reloads.</div>
      </div>
      <div class="stack-group">
        <div class="sg-label">Data Engine</div>
        <div class="sg-text">Industry-standard tabular data libraries handle everything from simple aggregations to complex transformations on datasets of any size.</div>
      </div>
      <div class="stack-group">
        <div class="sg-label">Visualization</div>
        <div class="sg-text">Interactive, publication-quality charts powered by a modern charting library — zoom, filter, and export any visual with a single click.</div>
      </div>
    </div>
    <div class="stack-row">
      <div class="stack-group">
        <div class="sg-label">AI &amp; Language Models</div>
        <div class="sg-text">A modular LLM abstraction layer connects to three leading providers — ultra-fast inference, frontier reasoning, and cost-efficient options are all supported interchangeably.</div>
      </div>
      <div class="stack-group">
        <div class="sg-label">Document Intelligence</div>
        <div class="sg-text">A vector database indexes document chunks semantically, enabling retrieval-augmented generation that finds the right answer from thousands of pages in milliseconds.</div>
      </div>
      <div class="stack-group">
        <div class="sg-label">Persistence &amp; Security</div>
        <div class="sg-text">A lightweight relational database stores all user data with parameterized queries and industry-standard password hashing — zero plaintext credentials.</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# CTA
st.markdown("""
<div class="cta">
  <div class="cta-h">Ready to Analyze Your Data?</div>
  <div class="cta-p">Get AI-powered insights from your datasets in minutes.</div>
</div>
""", unsafe_allow_html=True)

c1,c2,c3 = st.columns([3.5,1,3.5])
with c2:
    if st.button("Get Started", key="cta_btn"):
        st.switch_page("pages/login.py")

# FOOTER
st.markdown(f"""
<div class="foot">
  <div class="fb">InsightBot</div>
  <div class="fc">Final Year Project &nbsp;&middot;&nbsp; Avantika &amp; Geeta Bhatt &nbsp;&middot;&nbsp; </div>
  <div class="fc">AI-Powered Data Analytics Platform</div>
</div>
""", unsafe_allow_html=True)