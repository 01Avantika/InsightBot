"""
pages/dashboard_maker.py — InsightBot Dashboard Maker
Power BI / Tableau-style auto-dashboard from uploaded datasets.
Matches the InsightBot dark AI SaaS design system exactly.
"""

import streamlit as st
import sys, os, io, base64, json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from db.database import get_user_uploads, get_user_analyses, init_db
from utils.file_handler import format_file_size
from utils.eda import load_file
from utils.llm import generate_insights

init_db()

st.set_page_config(
    page_title="InsightBot — Dashboard Creator",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Auth ──────────────────────────────────────────────────────────────────────
if not st.session_state.get("user"):
    st.warning("Please login first.")
    st.switch_page("pages/login.py")

user = st.session_state["user"]

# ── Theme ─────────────────────────────────────────────────────────────────────
is_dark = st.session_state.get("dark_mode", True)

# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {{
    --bg-base:      #0B0C10;
    --bg-surface:   #12141a;
    --bg-card:      #161922;
    --bg-elevated:  #1c2030;
    --bg-hover:     #1f2638;
    --border:       #23263a;
    --border-l:     #2e3247;
    --purple:       #b794f4;
    --purple-d:     #7c3aed;
    --purple-dim:   rgba(183,148,244,0.10);
    --purple-glow:  rgba(183,148,244,0.22);
    --cyan:         #63b3ed;
    --green:        #34d399;
    --red:          #f87171;
    --amber:        #fbbf24;
    --pink:         #f472b6;
    --text-h:       #f1f5f9;
    --text-b:       #94a3b8;
    --text-dim:     #4b5675;
    --r-sm: 8px; --r-md: 12px; --r-lg: 16px; --r-xl: 20px;
}}

*, *::before, *::after {{ box-sizing: border-box; }}
html, body, .stApp {{
    font-family: 'Inter', sans-serif !important;
    background: var(--bg-base) !important;
    color: var(--text-h) !important;
    transition: background .35s, color .35s;
}}
#MainMenu, footer, header        {{ visibility: hidden !important; }}
[data-testid="stSidebarNav"]     {{ display: none !important; }}
[data-testid="stDecoration"]     {{ display: none !important; }}
.main .block-container           {{ padding: 0 !important; max-width: 100% !important; }}
section[data-testid="stMain"] > div {{ padding: 0 !important; }}

::-webkit-scrollbar              {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track        {{ background: var(--bg-base); }}
::-webkit-scrollbar-thumb        {{ background: var(--border-l); border-radius: 99px; }}
::-webkit-scrollbar-thumb:hover  {{ background: var(--purple-d); }}

/* ── Animations ── */
@keyframes fadeSlideUp {{ from{{opacity:0;transform:translateY(16px)}} to{{opacity:1;transform:none}} }}
@keyframes lp {{ 0%,100%{{opacity:1}} 50%{{opacity:.3}} }}
@keyframes gradMove {{ 0%{{background-position:0% 50%}} 50%{{background-position:100% 50%}} 100%{{background-position:0% 50%}} }}
@keyframes glowPulse {{
    0%,100% {{ box-shadow: 0 0 0 0 rgba(124,58,237,0); }}
    50%      {{ box-shadow: 0 0 20px 4px rgba(124,58,237,0.3); }}
}}

.anim-1 {{ animation: fadeSlideUp .42s ease both; }}
.anim-2 {{ animation: fadeSlideUp .42s .07s ease both; }}
.anim-3 {{ animation: fadeSlideUp .42s .14s ease both; }}
.anim-4 {{ animation: fadeSlideUp .42s .21s ease both; }}
.anim-5 {{ animation: fadeSlideUp .42s .28s ease both; }}
.anim-6 {{ animation: fadeSlideUp .42s .35s ease both; }}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {{
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
    width: 230px !important; min-width: 230px !important; max-width: 230px !important;
    padding: 0 !important;
}}
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebar"] .block-container {{ padding: 0 !important; }}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {{
    display:flex !important; align-items:center !important; gap:9px !important;
    padding:.5rem 1rem !important; border-radius:var(--r-sm) !important;
    margin:2px 10px !important; font-size:.82rem !important; font-weight:500 !important;
    color:var(--text-b) !important; text-decoration:none !important;
    transition:background .18s, color .18s, transform .15s !important; position:relative !important;
}}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {{
    background:var(--purple-dim) !important; color:var(--purple) !important; transform:translateX(3px) !important;
}}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] {{
    background:var(--purple-dim) !important; color:var(--purple) !important; font-weight:600 !important;
    border-left:3px solid var(--purple) !important; padding-left:calc(1rem - 3px) !important;
    box-shadow:0 0 8px var(--purple-glow) !important;
}}
[data-testid="stSidebar"] h3 {{
    font-size:.6rem !important; font-weight:700 !important; letter-spacing:.12em !important;
    text-transform:uppercase !important; color:var(--text-dim) !important;
    padding:1.2rem 1rem .4rem !important; margin:0 !important;
}}
[data-testid="stSidebar"] hr {{ border-color:var(--border) !important; margin:.25rem .75rem !important; }}
[data-testid="stSidebar"] div.stButton > button {{
    background:linear-gradient(135deg,#7c3aed,#5b8dee) !important;
    color:#fff !important; border:none !important; border-radius:var(--r-sm) !important;
    font-weight:600 !important; font-size:.82rem !important; padding:.55rem 1rem !important;
    width:100% !important; box-shadow:0 4px 12px rgba(124,58,237,.28) !important;
    transition:opacity .2s, transform .15s !important;
}}
[data-testid="stSidebar"] div.stButton > button:hover {{ opacity:.88 !important; transform:translateY(-1px) !important; }}

/* ── MAIN BUTTONS ── */
section[data-testid="stMain"] div.stButton > button {{
    background:linear-gradient(135deg,#7c3aed,#5b8dee) !important;
    color:#fff !important; border:none !important; border-radius:var(--r-sm) !important;
    font-weight:600 !important; font-size:.78rem !important; padding:.5rem 1rem !important;
    box-shadow:0 4px 14px rgba(124,58,237,.28) !important;
    transition:opacity .2s, transform .15s, box-shadow .2s !important;
    position:relative !important; overflow:hidden !important;
}}
section[data-testid="stMain"] div.stButton > button:hover {{
    opacity:.88 !important; transform:translateY(-2px) !important;
    box-shadow:0 8px 22px rgba(124,58,237,.45) !important;
}}
section[data-testid="stMain"] div.stButton > button:active {{
    transform:translateY(0) scale(.97) !important;
}}
[data-testid="stDownloadButton"] button {{
    background:transparent !important; border:1px solid var(--border-l) !important;
    color:var(--purple) !important; border-radius:var(--r-sm) !important;
    font-weight:600 !important; font-size:.78rem !important; transition:all .2s !important;
}}
[data-testid="stDownloadButton"] button:hover {{
    border-color:var(--purple) !important; background:var(--purple-dim) !important;
    transform:translateY(-1px) !important;
}}

/* ── SELECTBOX ── */
[data-baseweb="select"] > div {{
    background:var(--bg-elevated) !important; border:1px solid var(--border) !important;
    border-radius:var(--r-md) !important; color:var(--text-h) !important;
    font-size:.82rem !important;
}}
[data-baseweb="select"] > div:focus-within {{
    border-color:#7c3aed !important; box-shadow:0 0 0 3px rgba(124,58,237,.2) !important;
}}

/* ── EXPANDER ── */
[data-testid="stExpander"] {{
    background:var(--bg-card) !important; border:1px solid var(--border) !important;
    border-radius:var(--r-md) !important; margin-bottom:5px !important;
    transition:border-color .2s !important;
}}
[data-testid="stExpander"]:hover {{ border-color:rgba(183,148,244,.3) !important; }}
[data-testid="stExpander"] summary {{
    color:var(--text-h) !important; font-weight:600 !important; font-size:.82rem !important;
}}

/* ── ALERTS ── */
div[data-testid="stSuccessMessage"] {{
    background:rgba(52,211,153,.1) !important; border:1px solid rgba(52,211,153,.25) !important;
    color:#34d399 !important; border-radius:var(--r-md) !important;
}}
div[data-testid="stWarningMessage"] {{
    background:rgba(251,191,36,.1) !important; border:1px solid rgba(251,191,36,.25) !important;
    color:#fbbf24 !important; border-radius:var(--r-md) !important;
}}
div[data-testid="stInfoMessage"] {{
    background:rgba(99,179,237,.1) !important; border:1px solid rgba(99,179,237,.25) !important;
    color:#63b3ed !important; border-radius:var(--r-md) !important;
}}

[data-testid="stHorizontalBlock"] {{ gap: .85rem !important; }}

/* ──────────────────────────────────────────────────────
   DASHBOARD MAKER COMPONENT CLASSES
────────────────────────────────────────────────────── */

/* Sidebar logo */
.sb-logo {{
    display:flex; align-items:center; gap:10px;
    padding:1.25rem 1rem 1rem; border-bottom:1px solid var(--border); margin-bottom:.4rem;
}}
.sb-logo-icon {{
    width:32px; height:32px; border-radius:var(--r-sm);
    background:linear-gradient(135deg,#7c3aed,#63b3ed);
    display:flex; align-items:center; justify-content:center; font-size:1rem;
    animation:glowPulse 3s ease-in-out infinite;
}}
.sb-logo-name {{ font-size:.95rem; font-weight:800; color:var(--text-h); }}
.sb-logo-sub  {{ font-size:.55rem; color:var(--text-dim); letter-spacing:.12em; text-transform:uppercase; }}
.sb-user {{
    display:flex; align-items:center; gap:9px; padding:.6rem .85rem;
    border-radius:var(--r-md); background:var(--purple-dim);
    border:1px solid rgba(183,148,244,.14); margin:0 .6rem .45rem;
}}
.sb-avatar {{
    width:30px; height:30px; border-radius:50%;
    background:linear-gradient(135deg,#7c3aed,#63b3ed);
    color:#fff; font-weight:700; font-size:.82rem;
    display:flex; align-items:center; justify-content:center; flex-shrink:0;
}}
.sb-uname {{ font-size:.76rem; font-weight:600; color:var(--text-h); }}
.sb-email {{ font-size:.63rem; color:var(--text-dim);
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:138px; }}

/* Topbar */
.topbar {{
    display:flex; align-items:center; justify-content:space-between;
    padding:0 2rem; height:54px; border-bottom:1px solid var(--border);
    background:rgba(18,20,26,.95); backdrop-filter:blur(14px);
    position:sticky; top:0; z-index:200;
}}
.topbar-title {{ font-size:1rem; font-weight:700; color:var(--text-h);
    display:flex; align-items:center; gap:.6rem; }}
.topbar-right {{ display:flex; align-items:center; gap:.75rem; }}
.tb-avatar {{
    width:28px; height:28px; border-radius:50%;
    background:linear-gradient(135deg,#7c3aed,#63b3ed);
    color:#fff; font-weight:700; font-size:.75rem;
    display:flex; align-items:center; justify-content:center;
}}
.live-badge {{
    display:inline-flex; align-items:center; gap:5px;
    background:rgba(52,211,153,.1); border:1px solid rgba(52,211,153,.22);
    border-radius:99px; padding:.15rem .6rem;
    font-size:.6rem; font-weight:700; letter-spacing:.1em; color:#34d399; text-transform:uppercase;
}}
.live-dot {{ width:5px; height:5px; border-radius:50%; background:#34d399;
    animation:lp 1.6s ease-in-out infinite; }}

/* Page title */
.pg-title {{ font-size:1.5rem; font-weight:800; color:var(--text-h); margin-bottom:.15rem; }}
.pg-sub   {{ font-size:.82rem; color:var(--text-b); margin-bottom:1.6rem; }}

/* Section header */
.sec-hdr {{
    font-size:.82rem; font-weight:700; color:var(--text-h);
    display:flex; align-items:center; gap:.5rem;
    padding-left:.7rem; border-left:2.5px solid var(--purple); margin-bottom:.9rem;
}}
.sec-hdr small {{ font-size:.68rem; font-weight:400; color:var(--text-dim); margin-left:.25rem; }}

/* KPI metric card */
.kpi {{
    background:var(--bg-card); border:1px solid var(--border);
    border-radius:var(--r-lg); padding:1.2rem 1.4rem;
    position:relative; overflow:hidden; height:100%;
    transition:border-color .25s, transform .25s, box-shadow .25s;
    cursor:default;
}}
.kpi:hover {{
    border-color:rgba(183,148,244,.35); transform:translateY(-3px);
    box-shadow:0 10px 28px rgba(0,0,0,.5);
}}
.kpi::before {{
    content:''; position:absolute; top:0; left:-100%;
    width:55%; height:100%;
    background:linear-gradient(120deg,transparent,rgba(255,255,255,.035),transparent);
    transition:left .55s ease;
}}
.kpi:hover::before {{ left:160%; }}
.kpi::after {{
    content:''; position:absolute; top:0; right:0;
    width:68px; height:68px; border-radius:0 var(--r-lg) 0 68px;
    background:var(--purple-dim); pointer-events:none;
}}
.kpi-icon {{
    width:36px; height:36px; border-radius:var(--r-sm); background:var(--purple-dim);
    display:flex; align-items:center; justify-content:center;
    font-size:1.05rem; margin-bottom:.75rem;
    transition:transform .2s;
}}
.kpi:hover .kpi-icon {{ transform:scale(1.15) rotate(-5deg); }}
.kpi-label {{ font-size:.6rem; font-weight:700; letter-spacing:.1em;
    text-transform:uppercase; color:var(--text-dim); margin-bottom:.25rem; }}
.kpi-val {{ font-size:1.9rem; font-weight:800; color:var(--text-h);
    letter-spacing:-1px; line-height:1; }}
.kpi-unit {{ font-size:.85rem; font-weight:500; color:var(--text-b); margin-left:3px; }}
.kpi-badge {{
    display:inline-flex; align-items:center; gap:3px; font-size:.62rem;
    font-weight:700; padding:.12rem .45rem; border-radius:99px; margin-top:.4rem;
}}
.kb-up   {{ background:rgba(52,211,153,.12); color:#34d399; }}
.kb-down {{ background:rgba(248,113,113,.12); color:#f87171; }}
.kb-neu  {{ background:rgba(99,179,237,.12);  color:#63b3ed; }}
.kb-warn {{ background:rgba(251,191,36,.12);  color:#fbbf24; }}

/* Bento card */
.bc {{
    background:var(--bg-card); border:1px solid var(--border);
    border-radius:var(--r-lg); padding:1.25rem 1.4rem;
    transition:border-color .22s, box-shadow .22s;
}}
.bc:hover {{ border-color:rgba(183,148,244,.2); box-shadow:0 4px 24px rgba(0,0,0,.35); }}

/* AI insight card */
.ai-ins {{
    background:linear-gradient(135deg,rgba(124,58,237,.14),rgba(99,179,237,.06));
    border:1px solid rgba(183,148,244,.22); border-radius:var(--r-lg);
    padding:1.1rem 1.25rem; margin-bottom:.75rem;
    transition:border-color .22s, transform .22s;
    position:relative; overflow:hidden;
}}
.ai-ins:hover {{ border-color:rgba(183,148,244,.42); transform:translateY(-2px); }}
.ai-ins::before {{
    content:''; position:absolute; top:-25px; right:-25px;
    width:90px; height:90px; border-radius:50%;
    background:radial-gradient(circle,rgba(183,148,244,.13) 0%,transparent 70%);
    pointer-events:none;
}}
.ai-tag {{
    display:inline-flex; align-items:center; gap:5px;
    background:rgba(183,148,244,.1); border:1px solid rgba(183,148,244,.2);
    border-radius:99px; padding:.17rem .62rem;
    font-size:.58rem; font-weight:700; letter-spacing:.1em;
    color:var(--purple); text-transform:uppercase; margin-bottom:.65rem;
}}
.ai-dot {{ width:4px; height:4px; border-radius:50%; background:var(--purple);
    animation:lp 2s ease-in-out infinite; }}
.ai-title {{ font-size:.85rem; font-weight:700; color:var(--text-h); margin-bottom:.35rem; }}
.ai-body  {{ font-size:.76rem; color:var(--text-b); line-height:1.65; }}
.ai-num   {{ font-size:1.3rem; font-weight:800; color:var(--purple); }}

/* Dataset selector card */
.ds-select-card {{
    background:linear-gradient(135deg,rgba(124,58,237,.1),rgba(99,179,237,.05));
    border:1px solid rgba(183,148,244,.2); border-radius:var(--r-xl);
    padding:1.5rem 1.75rem; margin-bottom:1.5rem;
}}
.ds-pill {{
    display:inline-flex; align-items:center; gap:6px;
    background:rgba(183,148,244,.1); border:1px solid rgba(183,148,244,.22);
    border-radius:99px; padding:.22rem .75rem;
    font-size:.65rem; font-weight:700; letter-spacing:.08em;
    color:var(--purple); text-transform:uppercase; margin-bottom:.85rem;
}}

/* ── Generate button — purple gradient, matches UI perfectly ── */
.gen-btn-wrap div.stButton > button {{
    background: linear-gradient(135deg, #7c3aed 0%, #9b72e8 50%, #63b3ed 100%) !important;
    background-size: 200% auto !important;
    animation: gradMove 4s ease infinite !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--r-md) !important;
    font-size: .88rem !important;
    font-weight: 700 !important;
    padding: .7rem 1.5rem !important;
    box-shadow: 0 4px 20px rgba(124,58,237,.5), 0 0 0 1px rgba(183,148,244,.2) !important;
    letter-spacing: .04em !important;
    transition: opacity .2s, transform .18s, box-shadow .2s !important;
}}
.gen-btn-wrap div.stButton > button:hover {{
    opacity: .92 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(124,58,237,.65), 0 0 0 1px rgba(183,148,244,.35) !important;
}}
.gen-btn-wrap div.stButton > button:active {{
    transform: translateY(0) scale(.97) !important;
    box-shadow: 0 2px 10px rgba(124,58,237,.4) !important;
}}

/* Chart card */
.chart-card {{
    background:var(--bg-card); border:1px solid var(--border);
    border-radius:var(--r-lg); padding:1.1rem 1.25rem;
    transition:border-color .2s, box-shadow .2s;
}}
.chart-card:hover {{
    border-color:rgba(183,148,244,.25); box-shadow:0 6px 28px rgba(0,0,0,.4);
}}
.chart-title {{
    font-size:.78rem; font-weight:700; color:var(--text-h);
    margin-bottom:.75rem; display:flex; align-items:center; gap:.45rem;
}}
.chart-badge {{
    font-size:.58rem; font-weight:700; padding:.12rem .45rem;
    border-radius:99px; background:var(--purple-dim); color:var(--purple);
    letter-spacing:.06em; text-transform:uppercase;
}}

/* Stat table row */
.stat-row {{
    display:flex; align-items:center; justify-content:space-between;
    padding:.5rem .75rem; border-radius:var(--r-sm);
    transition:background .17s; margin-bottom:2px;
}}
.stat-row:hover {{ background:var(--bg-hover); }}
.stat-col {{ font-size:.75rem; color:var(--text-h); font-weight:600; flex:2; }}
.stat-val {{ font-size:.72rem; color:var(--text-b); flex:1; text-align:right; }}

/* Empty state */
.empty-state {{
    text-align:center; padding:3.5rem 1rem;
    color:var(--text-dim); font-size:.82rem;
}}
.empty-icon {{ font-size:2.5rem; margin-bottom:.75rem; opacity:.4; }}

/* Progress bar */
.prog-wrap {{ margin-bottom:.65rem; }}
.prog-top {{ display:flex; justify-content:space-between; margin-bottom:.3rem; }}
.prog-lbl {{ font-size:.72rem; color:var(--text-b); font-weight:500; }}
.prog-val {{ font-size:.72rem; color:var(--text-h); font-weight:700; }}
.prog-track {{ height:5px; background:var(--border); border-radius:99px; overflow:hidden; }}
.prog-fill {{ height:100%; border-radius:99px;
    background:linear-gradient(90deg,#7c3aed,#63b3ed); }}

/* Export card */
.export-card {{
    background:var(--bg-card); border:1px solid var(--border);
    border-radius:var(--r-lg); padding:1.25rem 1.4rem;
}}

/* page wrapper */
.pw {{ padding:0 2rem 2.5rem; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
u_name    = user.get("username", "User")
u_email   = user.get("email", "user@example.com")
u_initial = u_name[0].upper()

with st.sidebar:
    st.markdown(f"""
    <div class="sb-logo">
        <div class="sb-logo-icon">🤖</div>
        <div>
            <div class="sb-logo-name">InsightBot</div>
            <div class="sb-logo-sub">AI Intelligence</div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("### Navigation")
    st.page_link("pages/dashboard.py",        label="⬛  Dashboard")
    st.page_link("pages/analyze.py",          label="⬆  Upload & Analyze")
    st.page_link("pages/automl.py",           label="⚡  AutoML")
    st.page_link("pages/chat.py",             label="💬  Chat with Data")
    st.page_link("pages/history.py",          label="🕐  History")
    st.page_link("pages/Maker.py",  label="📊  Dashboard Creator")

    for _ in range(9): st.markdown("")
    st.markdown("<hr style='border-color:var(--border); margin:.25rem .5rem .5rem'/>",
                unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sb-user">
        <div class="sb-avatar">{u_initial}</div>
        <div style="min-width:0">
            <div class="sb-uname">{u_name}</div>
            <div class="sb-email">{u_email}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='padding:0 .6rem'>", unsafe_allow_html=True)
    if st.button("Logout", use_container_width=True, key="sb_logout"):
        st.session_state.clear()
        st.switch_page("pages/login.py")
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  TOPBAR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="topbar">
    <div class="topbar-title">
        📊 Dashboard Maker
        <span class="live-badge"><span class="live-dot"></span>Auto-Generate</span>
    </div>
    <div class="topbar-right">
        <div class="tb-avatar">{u_initial}</div>
    </div>
</div>""", unsafe_allow_html=True)

st.markdown('<div class="pw">', unsafe_allow_html=True)

st.markdown("""
<div class="pg-title anim-1">📊 Dashboard Maker</div>
<div class="pg-sub anim-1">Select a dataset and auto-generate a professional analytics dashboard
— KPIs, charts, AI insights, and export tools.</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: SMART COLUMN DETECTION
# ─────────────────────────────────────────────────────────────────────────────
def detect_columns(df: pd.DataFrame):
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols     = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_kw      = ["date", "time", "year", "month", "day", "created", "updated",
                    "timestamp", "dt", "period"]
    date_cols    = [c for c in df.columns
                    if any(k in c.lower() for k in date_kw)]
    for c in numeric_cols:
        if df[c].dropna().between(1900, 2100).all() and df[c].nunique() < 50:
            if c not in date_cols:
                date_cols.append(c)
    id_cols = [c for c in df.columns
               if any(k in c.lower() for k in ["id", "uuid", "key", "index"])
               or df[c].nunique() == len(df)]
    clean_num = [c for c in numeric_cols if c not in id_cols]
    clean_cat = [c for c in cat_cols     if c not in id_cols]
    return {
        "numeric":  clean_num,
        "category": clean_cat,
        "date":     date_cols,
        "id":       id_cols,
        "all_num":  numeric_cols,
    }


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: KPI GENERATION
# ─────────────────────────────────────────────────────────────────────────────
def build_kpis(df: pd.DataFrame, cols: dict) -> list:
    kpis = []
    rows, ncols = df.shape
    kpis.append({
        "icon": "📋", "label": "Total Records",
        "val": f"{rows:,}", "unit": "",
        "badge": "Dataset", "badge_cls": "kb-neu",
    })
    kpis.append({
        "icon": "📐", "label": "Total Columns",
        "val": str(ncols), "unit": "",
        "badge": f"{len(cols['numeric'])} numeric", "badge_cls": "kb-neu",
    })
    if cols["numeric"]:
        top_col = max(cols["numeric"], key=lambda c: df[c].std() if df[c].std() == df[c].std() else 0)
        mean_v  = df[top_col].mean()
        fmt     = f"{mean_v:,.1f}" if mean_v < 1e6 else f"{mean_v/1e6:.2f}M"
        kpis.append({
            "icon": "📈", "label": f"Avg {top_col[:18]}",
            "val": fmt, "unit": "",
            "badge": "▲ Key Metric", "badge_cls": "kb-up",
        })
    miss_pct = (df.isnull().sum().sum() / (rows * ncols) * 100)
    kpis.append({
        "icon": "🔍", "label": "Missing Data",
        "val": f"{miss_pct:.1f}", "unit": "%",
        "badge": "⚠ Warning" if miss_pct > 10 else "✓ Clean",
        "badge_cls": "kb-warn" if miss_pct > 10 else "kb-up",
    })
    dup_pct = df.duplicated().sum() / rows * 100
    kpis.append({
        "icon": "🔄", "label": "Duplicate Rows",
        "val": f"{df.duplicated().sum():,}", "unit": "",
        "badge": "⚠ Review" if dup_pct > 5 else "✓ OK",
        "badge_cls": "kb-warn" if dup_pct > 5 else "kb-up",
    })
    if cols["category"]:
        top_cat = max(cols["category"], key=lambda c: df[c].nunique())
        kpis.append({
            "icon": "🏷️", "label": f"Unique {top_cat[:16]}",
            "val": str(df[top_cat].nunique()), "unit": "",
            "badge": "Categories", "badge_cls": "kb-neu",
        })
    elif len(cols["numeric"]) > 1:
        kpis.append({
            "icon": "🔝", "label": f"Max {cols['numeric'][0][:16]}",
            "val": f"{df[cols['numeric'][0]].max():,.1f}", "unit": "",
            "badge": "Peak", "badge_cls": "kb-up",
        })
    return kpis[:6]


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: PLOTLY DARK THEME
# ─────────────────────────────────────────────────────────────────────────────
PLOTLY_DARK = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(22,25,34,0)",
    plot_bgcolor="rgba(22,25,34,0)",
    font_family="Inter",
    font_color="#94a3b8",
    title_font_color="#f1f5f9",
    legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#94a3b8"),
    margin=dict(l=20, r=20, t=40, b=20),
    colorway=["#b794f4","#63b3ed","#34d399","#fbbf24","#f87171","#f472b6","#a78bfa"],
    height=340,
)


def apply_theme(fig):
    fig.update_layout(**PLOTLY_DARK)
    fig.update_xaxes(gridcolor="#23263a", linecolor="#23263a", zerolinecolor="#23263a")
    fig.update_yaxes(gridcolor="#23263a", linecolor="#23263a", zerolinecolor="#23263a")
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: SMART CHART GENERATION
# ─────────────────────────────────────────────────────────────────────────────
def generate_charts(df: pd.DataFrame, cols: dict) -> list:
    charts = []
    num  = cols["numeric"]
    cat  = cols["category"]
    date = cols["date"]

    if date and num:
        d_col = date[0]
        n_col = num[0]
        try:
            tmp = df[[d_col, n_col]].dropna().copy()
            tmp[d_col] = pd.to_datetime(tmp[d_col], errors="coerce")
            tmp = tmp.dropna().sort_values(d_col)
            if len(tmp) > 1:
                fig = px.line(tmp, x=d_col, y=n_col,
                              title=f"Trend: {n_col} over {d_col}",
                              line_shape="spline")
                fig.update_traces(line_color="#b794f4", line_width=2.5,
                                  fill="tozeroy",
                                  fillcolor="rgba(183,148,244,0.08)")
                charts.append((f"📈 Trend — {n_col}", apply_theme(fig), "Trend"))
        except Exception:
            pass

    if cat and num:
        c_col = cat[0]
        n_col = num[0]
        try:
            tmp = (df.groupby(c_col)[n_col]
                   .mean().sort_values(ascending=False)
                   .head(15).reset_index())
            fig = px.bar(tmp, x=c_col, y=n_col,
                         title=f"Avg {n_col} by {c_col}",
                         color=n_col,
                         color_continuous_scale=["#1c2030","#7c3aed","#b794f4","#63b3ed"])
            fig.update_coloraxes(showscale=False)
            charts.append((f"📊 Bar — {n_col} by {c_col}", apply_theme(fig), "Comparison"))
        except Exception:
            pass

    if cat:
        c_col = cat[0]
        try:
            vc  = df[c_col].value_counts().head(10)
            fig = go.Figure(go.Pie(
                labels=vc.index, values=vc.values,
                hole=0.55,
                marker=dict(colors=["#b794f4","#63b3ed","#34d399","#fbbf24",
                                    "#f87171","#f472b6","#a78bfa","#7c3aed",
                                    "#2dd4bf","#fb923c"]),
            ))
            fig.update_traces(textposition="outside", textfont_color="#94a3b8",
                              hoverinfo="label+percent+value")
            charts.append((f"🥧 Distribution — {c_col}", apply_theme(fig), "Distribution"))
        except Exception:
            pass

    if num:
        n_col = num[0]
        try:
            fig = px.histogram(df, x=n_col, nbins=40,
                               title=f"Distribution of {n_col}",
                               color_discrete_sequence=["#b794f4"])
            fig.update_traces(marker_line_color="#7c3aed", marker_line_width=0.5)
            charts.append((f"📉 Histogram — {n_col}", apply_theme(fig), "Distribution"))
        except Exception:
            pass

    if len(num) >= 2:
        x_col, y_col = num[0], num[1]
        color_col    = cat[0] if cat else None
        try:
            sample = df.sample(min(2000, len(df)), random_state=42)
            fig = px.scatter(
                sample, x=x_col, y=y_col,
                color=color_col,
                title=f"Scatter: {x_col} vs {y_col}",
                opacity=0.65,
                color_discrete_sequence=["#b794f4","#63b3ed","#34d399","#fbbf24","#f87171"],
            )
            charts.append((f"🔵 Scatter — {x_col} vs {y_col}", apply_theme(fig), "Relationship"))
        except Exception:
            pass

    if len(num) >= 3:
        try:
            corr_cols = num[:12]
            corr = df[corr_cols].corr().round(2)
            fig  = go.Figure(go.Heatmap(
                z=corr.values, x=corr.columns, y=corr.columns,
                colorscale=[
                    [0.0, "#1c2030"], [0.3, "#2e1065"],
                    [0.5, "#7c3aed"], [0.7, "#a78bfa"],
                    [1.0, "#e9d5ff"],
                ],
                zmin=-1, zmax=1,
                text=corr.values, texttemplate="%{text}",
                textfont_size=9,
            ))
            fig.update_layout(title="Correlation Heatmap")
            charts.append(("🌡️ Correlation Heatmap", apply_theme(fig), "Correlation"))
        except Exception:
            pass

    if num:
        box_cols = num[:6]
        try:
            fig = go.Figure()
            colors = ["#b794f4","#63b3ed","#34d399","#fbbf24","#f87171","#f472b6"]
            for i, c in enumerate(box_cols):
                fig.add_trace(go.Box(
                    y=df[c].dropna(), name=c,
                    marker_color=colors[i % len(colors)],
                    line_color=colors[i % len(colors)],
                ))
            fig.update_layout(title="Box Plot — Numeric Spread", showlegend=False)
            charts.append(("📦 Box Plot — Spread", apply_theme(fig), "Distribution"))
        except Exception:
            pass

    if len(cat) >= 2 and num:
        c_col = cat[1]
        n_col = num[0]
        try:
            tmp = (df.groupby(c_col)[n_col]
                   .mean().sort_values(ascending=False).head(12).reset_index())
            fig = px.bar(tmp, x=n_col, y=c_col, orientation="h",
                         title=f"Avg {n_col} by {c_col}",
                         color=n_col,
                         color_continuous_scale=["#1c2030","#63b3ed","#b794f4"])
            fig.update_coloraxes(showscale=False)
            charts.append((f"📊 Horizontal — {c_col}", apply_theme(fig), "Comparison"))
        except Exception:
            pass

    return charts


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: AI INSIGHTS
# ─────────────────────────────────────────────────────────────────────────────
def build_ai_insights(df: pd.DataFrame, cols: dict, filename: str) -> list:
    insights = []
    num = cols["numeric"]
    cat = cols["category"]

    miss_pct = df.isnull().sum().sum() / df.size * 100
    insights.append({
        "tag": "Data Quality",
        "title": "Dataset Completeness",
        "stat": f"{100 - miss_pct:.1f}%",
        "body": (f"The dataset has {df.shape[0]:,} rows × {df.shape[1]} columns. "
                 f"{'Excellent data quality with only' if miss_pct < 5 else 'Attention needed —'} "
                 f"{miss_pct:.1f}% missing values. "
                 f"{'No action needed.' if miss_pct < 5 else 'Consider imputation before modeling.'}"),
    })

    if num:
        col   = num[0]
        skew  = df[col].skew()
        skew_label = ("right-skewed (long tail of high values)"
                      if skew > 1 else
                      "left-skewed (long tail of low values)"
                      if skew < -1 else "approximately normal")
        insights.append({
            "tag": "Distribution",
            "title": f"Shape of {col}",
            "stat": f"{skew:.2f} skew",
            "body": (f"**{col}** has mean {df[col].mean():,.2f} and std {df[col].std():,.2f}. "
                     f"Distribution is {skew_label}. "
                     f"{'Log-transform may improve model performance.' if abs(skew) > 1 else 'Good for linear models.'}"),
        })

    if cat:
        col = cat[0]
        top_val = df[col].value_counts().index[0]
        top_pct = df[col].value_counts(normalize=True).iloc[0] * 100
        insights.append({
            "tag": "Category",
            "title": f"Dominant Class — {col}",
            "stat": f"{top_pct:.1f}%",
            "body": (f"**'{top_val}'** is the most frequent value in **{col}**, "
                     f"representing {top_pct:.1f}% of all records. "
                     f"{'High concentration — watch for class imbalance in classification tasks.' if top_pct > 60 else 'Balanced distribution across categories.'}"),
        })

    if len(num) >= 2:
        corr = df[num[:8]].corr().abs()
        np.fill_diagonal(corr.values, 0)
        best_pair = corr.stack().idxmax()
        best_val  = corr.stack().max()
        insights.append({
            "tag": "Correlation",
            "title": "Strongest Relationship",
            "stat": f"r = {best_val:.2f}",
            "body": (f"**{best_pair[0]}** and **{best_pair[1]}** have the strongest correlation "
                     f"(r = {best_val:.2f}). "
                     f"{'Very strong signal — consider these as linked features.' if best_val > 0.7 else 'Moderate relationship worth exploring in scatter analysis.'}"),
        })

    try:
        from utils.eda import get_summary_text
        summary  = get_summary_text(df)
        llm_text = generate_insights(summary, filename)
        first_para = [l.strip() for l in llm_text.split("\n") if len(l.strip()) > 40]
        body = first_para[0] if first_para else llm_text[:280]
        insights.append({
            "tag": "AI Analysis",
            "title": "LLM-Generated Insight",
            "stat": "GPT",
            "body": body[:320],
        })
    except Exception:
        dups = df.duplicated().sum()
        insights.append({
            "tag": "Data Hygiene",
            "title": "Duplicate Records",
            "stat": str(dups),
            "body": (f"Found {dups} duplicate rows ({dups/len(df)*100:.1f}% of dataset). "
                     f"{'Remove duplicates before training ML models.' if dups > 0 else 'Dataset is duplicate-free — great for modeling.'}"),
        })

    return insights[:5]


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER: EXPORT
# ─────────────────────────────────────────────────────────────────────────────
def build_text_report(df: pd.DataFrame, filename: str, kpis: list,
                       insights: list, cols: dict) -> str:
    lines = [
        "=" * 60,
        "  INSIGHTBOT — AUTO DASHBOARD REPORT",
        "=" * 60,
        f"  Dataset  : {filename}",
        f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"  Shape    : {df.shape[0]:,} rows × {df.shape[1]} columns",
        "=" * 60, "",
        "── KPI SUMMARY ──────────────────────────────────────────────",
    ]
    for k in kpis:
        lines.append(f"  {k['label']:<28} {k['val']}{k['unit']}")
    lines += ["", "── NUMERIC SUMMARY ──────────────────────────────────────────"]
    if cols["numeric"]:
        try:
            desc = df[cols["numeric"]].describe().round(3)
            lines.append(desc.to_string())
        except Exception:
            pass
    lines += ["", "── AI INSIGHTS ──────────────────────────────────────────────"]
    for ins in insights:
        lines.append(f"\n  [{ins['tag']}] {ins['title']}")
        lines.append(f"  {ins['body'][:300]}")
    lines += ["", "── COLUMN DETAILS ───────────────────────────────────────────"]
    for c in df.columns:
        miss  = df[c].isnull().sum()
        uniq  = df[c].nunique()
        dtype = str(df[c].dtype)
        lines.append(f"  {c:<30} dtype={dtype:<12} missing={miss}  unique={uniq}")
    lines += ["", "=" * 60, "  Generated by InsightBot", "=" * 60]
    return "\n".join(lines)


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.describe(include="all").reset_index().to_csv(index=False).encode()


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 1 — DATASET SELECTOR
# ─────────────────────────────────────────────────────────────────────────────
uploads = get_user_uploads(user["id"])

st.markdown('<div class="ds-select-card anim-1">', unsafe_allow_html=True)
st.markdown("""
<div class="ds-pill">✦ Step 1 — Select Dataset</div>
<div style="font-size:.88rem;font-weight:700;color:var(--text-h);margin-bottom:.4rem">
    Choose a dataset to visualise</div>
<div style="font-size:.76rem;color:var(--text-b);margin-bottom:1rem">
    Only CSV / Excel files are supported for dashboard generation.</div>
""", unsafe_allow_html=True)

tabular_uploads = [u for u in uploads if u.get("file_type", "").lower() in ("csv","xlsx","xls")]

if not tabular_uploads:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">📂</div>
        No CSV or Excel files found.<br>
        <span style="color:var(--text-dim);font-size:.75rem">
            Upload a dataset on the Upload & Analyze page first.
        </span>
    </div>""", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)
    st.stop()

upload_labels = [
    f"{u['filename']}  ·  {format_file_size(u.get('file_size',0))}  ·  {u['uploaded_at'][:10]}"
    for u in tabular_uploads
]

sel_col, btn_col = st.columns([3, 1])
with sel_col:
    sel_idx = st.selectbox(
        "Dataset", range(len(upload_labels)),
        format_func=lambda i: upload_labels[i],
        key="dm_sel",
        label_visibility="collapsed",
    )
with btn_col:
    st.markdown('<div class="gen-btn-wrap">', unsafe_allow_html=True)
    generate = st.button("⚡  Generate Dashboard", key="dm_generate", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
selected_upload = tabular_uploads[sel_idx]
cache_key       = f"dm_df_{selected_upload['id']}"

if generate or cache_key in st.session_state:
    if generate or cache_key not in st.session_state:
        fp  = selected_upload["file_path"]
        ext = selected_upload["file_type"].lower()
        if not os.path.exists(fp):
            st.error("File not found on disk. Please re-upload.")
            st.stop()
        with st.spinner("🔄 Loading dataset…"):
            try:
                df = load_file(fp, ext)
                st.session_state[cache_key] = df
            except Exception as e:
                st.error(f"Failed to load file: {e}")
                st.stop()
    else:
        df = st.session_state[cache_key]

    filename = selected_upload["filename"]
    cols     = detect_columns(df)
    kpis     = build_kpis(df, cols)

    # ── SECTION 2 — KPI CARDS ────────────────────────────────────────────
    st.markdown("<div style='height:.6rem'></div>", unsafe_allow_html=True)
    st.markdown(f'<div class="sec-hdr anim-2">📌 KPI Summary <small>{filename}</small></div>',
                unsafe_allow_html=True)

    kpi_cols = st.columns(len(kpis))
    anim_cls = ["anim-2","anim-3","anim-4","anim-4","anim-5","anim-6"]
    for i, (kc, kpi) in enumerate(zip(kpi_cols, kpis)):
        with kc:
            st.markdown(f"""
            <div class="kpi {anim_cls[i]}">
                <div class="kpi-icon">{kpi['icon']}</div>
                <div class="kpi-label">{kpi['label']}</div>
                <div class="kpi-val">{kpi['val']}<span class="kpi-unit">{kpi['unit']}</span></div>
                <div class="kpi-badge {kpi['badge_cls']}">{kpi['badge']}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    # ── SECTION 3 — VISUALISATIONS ───────────────────────────────────────
    st.markdown('<div class="sec-hdr anim-3">📊 Visualizations <small>auto-generated from dataset structure</small></div>',
                unsafe_allow_html=True)

    with st.spinner("🎨 Generating charts…"):
        charts = generate_charts(df, cols)

    if not charts:
        st.info("Not enough data variety to generate charts. Ensure the dataset has numeric or categorical columns.")
    else:
        for i in range(0, len(charts), 2):
            c1, c2 = st.columns(2, gap="medium")
            for col_widget, idx in [(c1, i), (c2, i+1)]:
                if idx < len(charts):
                    title, fig, badge = charts[idx]
                    with col_widget:
                        st.markdown(f"""
                        <div class="chart-card">
                            <div class="chart-title">
                                {title}
                                <span class="chart-badge">{badge}</span>
                            </div>
                        </div>""", unsafe_allow_html=True)
                        fig.update_layout(height=340, margin=dict(l=10,r=10,t=36,b=10))
                        st.plotly_chart(fig, use_container_width=True,
                                        key=f"dm_chart_{idx}")

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    # ── SECTION 4 — AI INSIGHTS + DATA SUMMARY ───────────────────────────
    st.markdown('<div class="sec-hdr anim-4">✦ AI Insights <small>auto-generated · powered by LLM</small></div>',
                unsafe_allow_html=True)

    ins_col, stat_col = st.columns([1.15, 0.85], gap="large")

    with ins_col:
        with st.spinner("🤖 Generating AI insights…"):
            insights = build_ai_insights(df, cols, filename)

        for ins in insights:
            st.markdown(f"""
            <div class="ai-ins">
                <div class="ai-tag"><span class="ai-dot"></span>{ins['tag']}</div>
                <div class="ai-title">{ins['title']}
                    <span style="float:right;font-size:1.1rem;font-weight:800;
                         color:var(--purple)">{ins['stat']}</span>
                </div>
                <div class="ai-body">{ins['body']}</div>
            </div>""", unsafe_allow_html=True)

    with stat_col:
        st.markdown("""
        <div class="bc" style="margin-bottom:1rem">
            <div class="sec-hdr" style="margin:0 0 .85rem;border:none;padding:0;
                 font-size:.75rem">📋 Column Summary</div>
        """, unsafe_allow_html=True)

        n_num = len(cols["numeric"])
        n_cat = len(cols["category"])
        n_dat = len(cols["date"])
        total = df.shape[1]
        for label, val, color in [
            ("Numeric", n_num, "#b794f4"),
            ("Categorical", n_cat, "#63b3ed"),
            ("Date/Time", n_dat, "#34d399"),
            ("Other", total - n_num - n_cat - n_dat, "#fbbf24"),
        ]:
            pct = val / max(total, 1) * 100
            st.markdown(f"""
            <div class="prog-wrap">
                <div class="prog-top">
                    <span class="prog-lbl" style="color:{color}">{label}</span>
                    <span class="prog-val">{val} cols · {pct:.0f}%</span>
                </div>
                <div class="prog-track">
                    <div class="prog-fill" style="width:{pct}%;
                         background:linear-gradient(90deg,{color}88,{color})"></div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        if cols["numeric"]:
            st.markdown("""
            <div class="bc" style="margin-bottom:1rem">
                <div class="sec-hdr" style="margin:0 0 .75rem;border:none;padding:0;font-size:.75rem">
                    📈 Numeric Stats (Top 5 Columns)
                </div>""", unsafe_allow_html=True)

            for c in cols["numeric"][:5]:
                mean_v = df[c].mean()
                std_v  = df[c].std()
                null_v = df[c].isnull().sum()
                st.markdown(f"""
                <div class="stat-row">
                    <span class="stat-col">{c[:22]}</span>
                    <span class="stat-val">μ={mean_v:,.1f}  σ={std_v:,.1f}  ∅{null_v}</span>
                </div>""", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        miss_series  = df.isnull().sum().sort_values(ascending=False)
        miss_nonzero = miss_series[miss_series > 0]
        if len(miss_nonzero):
            st.markdown("""
            <div class="bc">
                <div class="sec-hdr" style="margin:0 0 .75rem;border:none;padding:0;font-size:.75rem">
                    🔍 Missing Values
                </div>""", unsafe_allow_html=True)
            for c, cnt in miss_nonzero.head(6).items():
                pct   = cnt / len(df) * 100
                color = "#f87171" if pct > 30 else "#fbbf24" if pct > 10 else "#63b3ed"
                st.markdown(f"""
                <div class="prog-wrap">
                    <div class="prog-top">
                        <span class="prog-lbl">{str(c)[:22]}</span>
                        <span class="prog-val" style="color:{color}">{cnt} ({pct:.1f}%)</span>
                    </div>
                    <div class="prog-track">
                        <div class="prog-fill" style="width:{min(pct,100)}%;
                             background:linear-gradient(90deg,{color}66,{color})"></div>
                    </div>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="bc">
                <div style="text-align:center;padding:1.25rem;color:#34d399;font-size:.8rem">
                    ✅ No missing values — dataset is complete!
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    # ── SECTION 5 — DATA EXPLORER ─────────────────────────────────────────
    st.markdown('<div class="sec-hdr">🗃️ Data Explorer</div>', unsafe_allow_html=True)

    with st.expander("📋 Preview first 100 rows", expanded=False):
        st.dataframe(df.head(100), use_container_width=True, height=320)

    with st.expander("📈 Descriptive Statistics", expanded=False):
        num_df = df.select_dtypes(include="number")
        if not num_df.empty:
            st.dataframe(num_df.describe().round(3), use_container_width=True)

    with st.expander("🏷️ Categorical Breakdown", expanded=False):
        for c in cols["category"][:4]:
            st.markdown(f"**{c}**")
            vc = df[c].value_counts().head(10).reset_index()
            vc.columns = [c, "count"]
            st.dataframe(vc, use_container_width=True, height=200)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    # ── SECTION 6 — EXPORT ────────────────────────────────────────────────
    st.markdown('<div class="sec-hdr">📥 Export & Download</div>',
                unsafe_allow_html=True)

    st.markdown('<div class="export-card">', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-size:.8rem;color:var(--text-b);margin-bottom:1rem">
        Download your dashboard data and reports in multiple formats.
    </div>""", unsafe_allow_html=True)

    e1, e2, e3 = st.columns(3)
    text_report = build_text_report(df, filename, kpis, insights, cols)

    with e1:
        st.markdown("""
        <div style="margin-bottom:.5rem">
            <div style="font-size:.75rem;font-weight:700;color:var(--text-h);margin-bottom:.2rem">
                📄 Summary Report
            </div>
            <div style="font-size:.68rem;color:var(--text-dim)">
                Full KPIs, stats & AI insights as .txt
            </div>
        </div>""", unsafe_allow_html=True)
        st.download_button(
            "⬇  Download Report (.txt)",
            data=text_report.encode(),
            file_name=f"insightbot_dashboard_{filename.split('.')[0]}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with e2:
        st.markdown("""
        <div style="margin-bottom:.5rem">
            <div style="font-size:.75rem;font-weight:700;color:var(--text-h);margin-bottom:.2rem">
                📊 Stats Export
            </div>
            <div style="font-size:.68rem;color:var(--text-dim)">
                Descriptive statistics as .csv
            </div>
        </div>""", unsafe_allow_html=True)
        st.download_button(
            "⬇  Download Stats (.csv)",
            data=df_to_csv_bytes(df),
            file_name=f"stats_{filename.split('.')[0]}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with e3:
        st.markdown("""
        <div style="margin-bottom:.5rem">
            <div style="font-size:.75rem;font-weight:700;color:var(--text-h);margin-bottom:.2rem">
                🗄️ Raw Data Export
            </div>
            <div style="font-size:.68rem;color:var(--text-dim)">
                Full cleaned dataset as .csv
            </div>
        </div>""", unsafe_allow_html=True)
        st.download_button(
            "⬇  Download Data (.csv)",
            data=df.to_csv(index=False).encode(),
            file_name=f"data_{filename.split('.')[0]}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown(f"""
    <div class="empty-state anim-2">
        <div class="empty-icon">📊</div>
        <div style="font-size:.95rem;font-weight:700;color:var(--text-h);margin-bottom:.5rem">
            Ready to generate your dashboard
        </div>
        <div style="font-size:.8rem;color:var(--text-b);max-width:380px;margin:0 auto">
            Select a dataset above and click
            <b style="color:#b794f4">⚡ Generate Dashboard</b> to auto-build
            KPI cards, charts, AI insights, and export tools.
        </div>
        <div style="margin-top:1.5rem;display:flex;justify-content:center;gap:.75rem;flex-wrap:wrap">
            <span style="background:rgba(183,148,244,.1);border:1px solid rgba(183,148,244,.2);
                 border-radius:99px;padding:.25rem .75rem;font-size:.68rem;color:var(--purple)">
                📈 Trend Charts
            </span>
            <span style="background:rgba(99,179,237,.1);border:1px solid rgba(99,179,237,.2);
                 border-radius:99px;padding:.25rem .75rem;font-size:.68rem;color:#63b3ed">
                📊 Bar & Pie Charts
            </span>
            <span style="background:rgba(52,211,153,.1);border:1px solid rgba(52,211,153,.2);
                 border-radius:99px;padding:.25rem .75rem;font-size:.68rem;color:#34d399">
                🌡️ Heatmaps
            </span>
            <span style="background:rgba(251,191,36,.1);border:1px solid rgba(251,191,36,.2);
                 border-radius:99px;padding:.25rem .75rem;font-size:.68rem;color:#fbbf24">
                ✦ AI Insights
            </span>
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)  # close .pw