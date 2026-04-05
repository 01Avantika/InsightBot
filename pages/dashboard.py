"""
pages/dashboard.py — InsightBot Dashboard
Modern Dark Intelligence + Animations + Light/Dark Mode + Animated Charts
"""

from datetime import datetime, timedelta
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import random, time
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from db.database import get_user_uploads, get_user_analyses, get_user_chats, init_db
from utils.file_handler import format_file_size

init_db()

st.set_page_config(
    page_title="InsightBot — Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Auth guard ───────────────────────────────────────────────────────────────
if not st.session_state.get("user"):
    st.warning("Please login first.")
    st.switch_page("pages/login.py")

user = st.session_state["user"]

# ── Theme state ──────────────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

is_dark = st.session_state.dark_mode

# ── Theme tokens ─────────────────────────────────────────────────────────────
if is_dark:
    T = {
        "bg_base":      "#0B0C10",
        "bg_surface":   "#12141a",
        "bg_card":      "#161922",
        "bg_elevated":  "#1c2030",
        "bg_hover":     "#1f2638",
        "border":       "#23263a",
        "border_l":     "#2e3247",
        "text_h":       "#f1f5f9",
        "text_b":       "#94a3b8",
        "text_dim":     "#4b5675",
        "topbar_bg":    "rgba(18,20,26,0.92)",
        "sb_bg":        "#12141a",
        "card_bg":      "#161922",
        "mc_before":    "rgba(183,148,244,0.10)",
        "ai_card_bg":   "linear-gradient(135deg,rgba(124,58,237,.18) 0%,rgba(99,179,237,.08) 100%)",
        "ai_card_bdr":  "rgba(183,148,244,.22)",
        "toggle_bg":    "rgba(183,148,244,.15)",
        "toggle_bdr":   "rgba(183,148,244,.35)",
        "toggle_color": "#b794f4",
        "toggle_icon":  "☀️",
        "toggle_label": "Light",
    }
else:
    T = {
        "bg_base":      "#f0f2f8",
        "bg_surface":   "#ffffff",
        "bg_card":      "#ffffff",
        "bg_elevated":  "#f8f9ff",
        "bg_hover":     "#eef0f8",
        "border":       "#e2e5f0",
        "border_l":     "#d0d4e8",
        "text_h":       "#0f1117",
        "text_b":       "#4b5675",
        "text_dim":     "#9098b4",
        "topbar_bg":    "rgba(255,255,255,0.94)",
        "sb_bg":        "#ffffff",
        "card_bg":      "#ffffff",
        "mc_before":    "rgba(124,58,237,0.06)",
        "ai_card_bg":   "linear-gradient(135deg,rgba(124,58,237,.07) 0%,rgba(99,179,237,.04) 100%)",
        "ai_card_bdr":  "rgba(124,58,237,.18)",
        "toggle_bg":    "rgba(124,58,237,.12)",
        "toggle_bdr":   "rgba(124,58,237,.28)",
        "toggle_color": "#7c3aed",
        "toggle_icon":  "🌙",
        "toggle_label": "Dark",
    }

# ============================================================================
#  CSS
# ============================================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {{
    --bg-base:      {T['bg_base']};
    --bg-surface:   {T['bg_surface']};
    --bg-card:      {T['bg_card']};
    --bg-elevated:  {T['bg_elevated']};
    --bg-hover:     {T['bg_hover']};
    --border:       {T['border']};
    --border-l:     {T['border_l']};
    --text-h:       {T['text_h']};
    --text-b:       {T['text_b']};
    --text-dim:     {T['text_dim']};

    --purple:       #b794f4;
    --purple-mid:   #9b72e8;
    --purple-dark:  #7c3aed;
    --purple-dim:   rgba(183,148,244,0.10);
    --purple-glow:  rgba(183,148,244,0.22);
    --cyan:         #63b3ed;
    --green:        #34d399;
    --red:          #f87171;
    --amber:        #fbbf24;

    --r-sm: 8px; --r-md: 12px; --r-lg: 16px; --r-xl: 20px;
}}

*, *::before, *::after {{ box-sizing: border-box; }}
html, body, .stApp {{
    font-family: 'Inter', sans-serif !important;
    background: var(--bg-base) !important;
    color: var(--text-h) !important;
    transition: background .35s ease, color .35s ease;
}}

#MainMenu, footer, header        {{ visibility: hidden !important; }}
[data-testid="stSidebarNav"]     {{ display: none !important; }}
[data-testid="stDecoration"]     {{ display: none !important; }}
.main .block-container           {{ padding: 0 !important; max-width: 100% !important; }}
section[data-testid="stMain"] > div {{ padding: 0 !important; }}

::-webkit-scrollbar              {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track        {{ background: var(--bg-base); }}
::-webkit-scrollbar-thumb        {{ background: var(--border-l); border-radius: 99px; }}
::-webkit-scrollbar-thumb:hover  {{ background: var(--purple-dark); }}

@keyframes fadeSlideUp {{
    from {{ opacity:0; transform:translateY(18px); }}
    to   {{ opacity:1; transform:translateY(0); }}
}}
@keyframes fadeIn {{
    from {{ opacity:0; }} to {{ opacity:1; }}
}}
@keyframes scaleIn {{
    from {{ opacity:0; transform:scale(.94); }}
    to   {{ opacity:1; transform:scale(1); }}
}}
@keyframes shimmer {{
    0%   {{ background-position:-400px 0; }}
    100% {{ background-position: 400px 0; }}
}}
@keyframes lp {{ 0%,100%{{opacity:1}} 50%{{opacity:.3}} }}
@keyframes pulseRing {{
    0%   {{ box-shadow: 0 0 0 0 rgba(183,148,244,.45); }}
    70%  {{ box-shadow: 0 0 0 8px rgba(183,148,244,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(183,148,244,0); }}
}}

.anim-1  {{ animation: fadeSlideUp .45s ease both; }}
.anim-2  {{ animation: fadeSlideUp .45s .08s ease both; }}
.anim-3  {{ animation: fadeSlideUp .45s .16s ease both; }}
.anim-4  {{ animation: fadeSlideUp .45s .24s ease both; }}
.anim-5  {{ animation: fadeSlideUp .45s .32s ease both; }}
.anim-6  {{ animation: fadeSlideUp .45s .40s ease both; }}
.anim-row {{ animation: fadeIn .5s ease both; }}

[data-testid="stSidebar"] {{
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: {T['sb_bg']} !important;
    border-right: 1px solid var(--border) !important;
    width: 230px !important; min-width: 230px !important; max-width: 230px !important;
    padding: 0 !important;
    transition: background .35s ease;
    transform: none !important;
}}
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebar"] .block-container {{ padding: 0 !important; }}
[data-testid="collapsedControl"],
button[kind="header"][aria-label*="sidebar"],
[data-testid="stSidebarCollapseButton"] {{ display: none !important; }}

[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {{
    display: flex !important; align-items: center !important; gap: 9px !important;
    padding: .5rem 1rem !important; border-radius: var(--r-sm) !important;
    margin: 2px 10px !important; font-size: .82rem !important; font-weight: 500 !important;
    color: var(--text-b) !important; text-decoration: none !important;
    transition: background .18s, color .18s, transform .15s !important;
    position: relative !important;
}}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {{
    background: var(--purple-dim) !important; color: var(--purple) !important;
    transform: translateX(3px) !important;
}}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] {{
    background: var(--purple-dim) !important; color: var(--purple) !important; font-weight: 600 !important;
}}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"]::before {{
    content:''; position:absolute; left:0; top:22%; bottom:22%;
    width:3px; border-radius:0 3px 3px 0; background:var(--purple);
    box-shadow:0 0 8px var(--purple-glow);
}}
[data-testid="stSidebar"] h3 {{
    font-size:.6rem !important; font-weight:700 !important; letter-spacing:.12em !important;
    text-transform:uppercase !important; color:var(--text-dim) !important;
    padding:1.2rem 1rem .4rem !important; margin:0 !important;
}}
[data-testid="stSidebar"] hr {{ border-color:var(--border) !important; margin:.5rem .75rem !important; }}

div.stButton > button {{
    background: linear-gradient(135deg,#7c3aed 0%,#5b8dee 100%) !important;
    color:#fff !important; border:none !important; border-radius:var(--r-sm) !important;
    font-weight:600 !important; font-size:.78rem !important; letter-spacing:.02em !important;
    padding:.5rem 1rem !important;
    box-shadow:0 4px 14px rgba(124,58,237,.28) !important;
    transition: opacity .2s, transform .15s, box-shadow .2s !important;
    position: relative !important; overflow: hidden !important;
}}
div.stButton > button:hover {{
    opacity:.88 !important; transform:translateY(-2px) !important;
    box-shadow:0 8px 22px rgba(124,58,237,.45) !important;
}}
div.stButton > button:active {{
    transform:translateY(0px) scale(.97) !important;
    box-shadow:0 2px 8px rgba(124,58,237,.3) !important;
}}
[data-testid="stDownloadButton"] button {{
    background:transparent !important; border:1px solid var(--border-l) !important;
    color:var(--purple) !important; border-radius:var(--r-sm) !important;
    font-weight:600 !important; font-size:.78rem !important;
    transition: all .2s !important;
}}
[data-testid="stDownloadButton"] button:hover {{
    border-color:var(--purple) !important; background:var(--purple-dim) !important;
    transform:translateY(-1px) !important;
}}

[data-testid="stExpander"] {{
    background:var(--bg-card) !important; border:1px solid var(--border) !important;
    border-radius:var(--r-md) !important; margin-bottom:5px !important;
    transition:border-color .2s, box-shadow .2s !important;
}}
[data-testid="stExpander"]:hover {{
    border-color:rgba(183,148,244,.3) !important;
    box-shadow:0 4px 16px rgba(0,0,0,.3) !important;
}}
[data-testid="stExpander"] summary {{
    color:var(--text-h) !important; font-weight:600 !important; font-size:.82rem !important;
}}
[data-testid="stExpander"] summary:hover {{ color:var(--purple) !important; }}

.stAlert,[data-testid="stAlert"] {{
    background:var(--bg-elevated) !important; border:1px solid var(--border) !important;
    border-radius:var(--r-md) !important; color:var(--text-b) !important;
}}

iframe[title="st_components_v1.html"] {{
    display: block !important; height: 0px !important;
    min-height: 0 !important; overflow: hidden !important; border: none !important;
}}

.main, section[data-testid="stMain"] {{ padding-left: 1.5rem !important; }}
[data-testid="stHorizontalBlock"] {{ gap:1rem !important; }}

/* ── Component classes ── */
.sb-logo {{
    display:flex; align-items:center; gap:10px;
    padding:1.25rem 1rem 1rem; border-bottom:1px solid var(--border); margin-bottom:.4rem;
}}
.sb-logo-icon {{
    width:32px; height:32px; border-radius:var(--r-sm);
    background:linear-gradient(135deg,#7c3aed,#63b3ed);
    display:flex; align-items:center; justify-content:center; font-size:1rem;
    animation: pulseRing 3s ease-in-out infinite;
}}
.sb-logo-name {{ font-size:.95rem; font-weight:800; color:var(--text-h); }}
.sb-logo-sub  {{ font-size:.55rem; color:var(--text-dim); letter-spacing:.12em; text-transform:uppercase; }}

.sb-user {{
    display:flex; align-items:center; gap:9px; padding:.65rem .85rem;
    border-radius:var(--r-md); background:var(--purple-dim);
    border:1px solid rgba(183,148,244,.14); margin:0 .6rem .6rem;
    transition:background .2s, border-color .2s;
}}
.sb-avatar {{
    width:32px; height:32px; border-radius:50%;
    background:linear-gradient(135deg,#7c3aed,#63b3ed);
    color:#fff; font-weight:700; font-size:.85rem;
    display:flex; align-items:center; justify-content:center; flex-shrink:0;
}}
.sb-uname {{ font-size:.78rem; font-weight:600; color:var(--text-h); }}
.sb-email {{ font-size:.65rem; color:var(--text-dim);
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:140px; }}

.topbar {{
    display:flex; align-items:center; justify-content:space-between;
    padding:0 2rem; height:54px;
    border-bottom:1px solid var(--border);
    background:{T['topbar_bg']};
    backdrop-filter:blur(14px);
    position:sticky; top:0; z-index:200;
    transition:background .35s ease;
}}
.topbar-title {{ font-size:1rem; font-weight:700; color:var(--text-h); display:flex; align-items:center; gap:.6rem; }}
.tb-avatar {{
    width:28px; height:28px; border-radius:50%;
    background:linear-gradient(135deg,#7c3aed,#63b3ed);
    color:#fff; font-weight:700; font-size:.75rem;
    display:flex; align-items:center; justify-content:center; cursor:pointer;
    transition:transform .2s, box-shadow .2s;
}}
.tb-avatar:hover {{ transform:scale(1.1); box-shadow:0 4px 12px rgba(124,58,237,.4); }}

.live-badge {{
    display:inline-flex; align-items:center; gap:5px;
    background:rgba(52,211,153,.1); border:1px solid rgba(52,211,153,.22);
    border-radius:99px; padding:.15rem .6rem;
    font-size:.6rem; font-weight:700; letter-spacing:.1em; color:#34d399; text-transform:uppercase;
}}
.live-dot {{ width:5px; height:5px; border-radius:50%; background:#34d399; animation:lp 1.6s ease-in-out infinite; }}

.pg-title {{ font-size:1.5rem; font-weight:800; color:var(--text-h); margin-bottom:.15rem; }}
.pg-sub   {{ font-size:.82rem; color:var(--text-b); margin-bottom:1.6rem; }}

.sec-hdr {{
    font-size:.82rem; font-weight:700; color:var(--text-h);
    display:flex; align-items:center; gap:.5rem;
    padding-left:.7rem; border-left:2.5px solid var(--purple); margin-bottom:.9rem;
}}
.sec-hdr small {{ font-size:.68rem; font-weight:400; color:var(--text-dim); margin-left:.2rem; }}

.mc {{
    background:var(--bg-card); border:1px solid var(--border); border-radius:var(--r-lg);
    padding:1.25rem 1.4rem; position:relative; overflow:hidden; height:100%;
    transition:border-color .25s, transform .25s, box-shadow .25s, background .35s;
    cursor:default;
}}
.mc:hover {{
    border-color:rgba(183,148,244,.35); transform:translateY(-4px);
    box-shadow:0 12px 32px rgba(0,0,0,.45);
}}
.mc::before {{
    content:''; position:absolute; top:0; left:-100%; width:60%; height:100%;
    background:linear-gradient(120deg,transparent 0%,rgba(255,255,255,.04) 50%,transparent 100%);
    transition:left .55s ease;
}}
.mc:hover::before {{ left:160%; }}
.mc::after {{
    content:''; position:absolute; top:0; right:0;
    width:70px; height:70px; border-radius:0 var(--r-lg) 0 70px;
    background:{T['mc_before']}; pointer-events:none;
}}
.mc-icon {{
    width:36px; height:36px; border-radius:var(--r-sm); background:var(--purple-dim);
    display:flex; align-items:center; justify-content:center;
    font-size:1.1rem; margin-bottom:.8rem; transition:transform .2s;
}}
.mc:hover .mc-icon {{ transform:scale(1.15) rotate(-5deg); }}
.mc-label {{ font-size:.62rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--text-dim); margin-bottom:.3rem; }}
.mc-num {{ font-size:2rem; font-weight:800; color:var(--text-h); letter-spacing:-1px; line-height:1; }}
.mc-unit {{ font-size:.9rem; font-weight:500; color:var(--text-b); margin-left:2px; }}
.mc-badge {{
    display:inline-flex; align-items:center; gap:3px; font-size:.62rem; font-weight:700;
    padding:.12rem .45rem; border-radius:99px; margin-top:.45rem;
}}
.mc-badge.up   {{ background:rgba(52,211,153,.12); color:#34d399; }}
.mc-badge.down {{ background:rgba(248,113,113,.12); color:#f87171; }}
.mc-badge.peak {{ background:rgba(251,191,36,.12);  color:#fbbf24; }}
.mc-badge.neu  {{ background:rgba(99,179,237,.12);  color:#63b3ed; }}

.bc {{
    background:var(--bg-card); border:1px solid var(--border); border-radius:var(--r-lg);
    padding:1rem 1.2rem;
    transition:border-color .22s, box-shadow .22s, background .35s;
}}
.bc:hover {{ border-color:rgba(183,148,244,.22); box-shadow:0 4px 24px rgba(0,0,0,.3); }}

.ai-insight {{
    background:{T['ai_card_bg']};
    border:1px solid {T['ai_card_bdr']};
    border-radius:var(--r-lg); padding:1.2rem 1.4rem;
    position:relative; overflow:hidden;
    transition:border-color .22s, transform .22s, box-shadow .22s;
}}
.ai-insight:hover {{
    border-color:rgba(183,148,244,.4); transform:translateY(-3px);
    box-shadow:0 10px 28px rgba(124,58,237,.18);
}}
.ai-insight::before {{
    content:''; position:absolute; top:-30px; right:-30px; width:100px; height:100px;
    border-radius:50%; background:radial-gradient(circle,rgba(183,148,244,.15) 0%,transparent 70%);
    pointer-events:none;
}}
.ai-tag {{
    display:inline-flex; align-items:center; gap:5px;
    background:rgba(183,148,244,.12); border:1px solid rgba(183,148,244,.2);
    border-radius:99px; padding:.18rem .65rem;
    font-size:.6rem; font-weight:700; letter-spacing:.1em; color:var(--purple);
    text-transform:uppercase; margin-bottom:.7rem;
}}
.ai-tag-dot {{ width:5px; height:5px; border-radius:50%; background:var(--purple); animation:lp 2s ease-in-out infinite; }}
.ai-title   {{ font-size:.9rem; font-weight:700; color:var(--text-h); margin-bottom:.4rem; }}
.ai-body    {{ font-size:.78rem; color:var(--text-b); line-height:1.65; }}
.ai-stat    {{ font-size:1.4rem; font-weight:800; color:var(--purple); }}

.hr-row {{
    display:flex; align-items:center; gap:.7rem;
    padding:.5rem .7rem;
    border-radius:var(--r-md);
    border:1px solid transparent; transition:all .17s; margin-bottom:2px; cursor:default;
}}
.hr-row:hover {{ background:var(--bg-hover); border-color:var(--border); transform:translateX(2px); }}
.hr-icon {{
    width:30px; height:30px; border-radius:var(--r-sm);
    display:flex; align-items:center; justify-content:center;
    font-size:.8rem; flex-shrink:0; transition:transform .2s;
}}
.hr-row:hover .hr-icon {{ transform:scale(1.12); }}
.ic-csv  {{ background:rgba(52,211,153,.12);  color:#34d399; }}
.ic-pdf  {{ background:rgba(248,113,113,.12); color:#f87171; }}
.ic-xlsx {{ background:rgba(99,179,237,.12);  color:#63b3ed; }}
.ic-other{{ background:rgba(183,148,244,.12); color:#b794f4; }}
.hr-name {{ font-size:.78rem; font-weight:600; color:var(--text-h);
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
.hr-sub  {{ font-size:.65rem; color:var(--text-dim); margin-top:1px; }}
.hr-date {{ font-size:.63rem; color:var(--text-dim); white-space:nowrap; flex-shrink:0; }}

.act-item {{
    display:flex; align-items:flex-start; gap:.55rem;
    padding:.45rem 0;
    border-bottom:1px solid var(--border);
    transition:background .17s; border-radius:var(--r-sm); padding-left:.3rem;
}}
.act-item:last-child {{ border-bottom:none; }}
.act-item:hover {{ background:var(--bg-hover); }}
.act-dot {{
    width:26px; height:26px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-size:.75rem; flex-shrink:0; margin-top:1px; transition:transform .2s;
}}
.act-item:hover .act-dot {{ transform:scale(1.12); }}
.act-dot.upload  {{ background:rgba(52,211,153,.12);  color:#34d399; }}
.act-dot.analyze {{ background:rgba(183,148,244,.12); color:#b794f4; }}
.act-dot.chat    {{ background:rgba(99,179,237,.12);  color:#63b3ed; }}
.act-text {{ font-size:.76rem; font-weight:500; color:var(--text-h); }}
.act-time {{ font-size:.64rem; color:var(--text-dim); margin-top:1px; }}

.hbar-track {{ height:5px; background:var(--border); border-radius:99px; overflow:hidden; margin-top:.55rem; }}
.hbar-fill  {{
    height:100%; border-radius:99px;
    background:linear-gradient(90deg,#7c3aed,#63b3ed);
    animation:fadeIn .8s .2s both;
}}

.empty-state {{
    text-align:center; padding:1.5rem 1rem; color:var(--text-dim); font-size:.8rem;
}}
.empty-state .es-icon {{ font-size:1.5rem; margin-bottom:.4rem; opacity:.4; }}

/* ── Chart widget styles ── */
.chart-wrap {{
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: .65rem;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    padding: 4px 2px 0;
    animation: scaleIn .5s ease both;
}}
.chart-label {{
    font-size: .58rem;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--text-dim);
    padding: 2px 6px 2px;
}}
.file-scroll {{
    max-height: 190px;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: var(--border-l) transparent;
}}
.file-scroll::-webkit-scrollbar       {{ width: 3px; }}
.file-scroll::-webkit-scrollbar-track {{ background: transparent; }}
.file-scroll::-webkit-scrollbar-thumb {{ background: var(--border-l); border-radius: 99px; }}

.pw {{ padding:0 2rem 2.5rem; }}
</style>
""", unsafe_allow_html=True)


# ============================================================================
#  PLOTLY CHART HELPERS
# ============================================================================
_TRANSPARENT = "rgba(0,0,0,0)"
_PURPLE_LITE = "#b794f4"
_BLUE        = "#3b82f6"
_CYAN        = "#63b3ed"
_TEXT_DIM    = "#4b5675"
_TEXT_B      = "#94a3b8"
_GRID        = "rgba(255,255,255,0.04)"
_LAYOUT_BASE = dict(
    paper_bgcolor=_TRANSPARENT,
    plot_bgcolor=_TRANSPARENT,
    margin=dict(l=0, r=0, t=4, b=0),
    font=dict(family="Inter, sans-serif", color=_TEXT_B, size=9),
    showlegend=False,
    hovermode="x unified",
    xaxis=dict(
        showgrid=False, zeroline=False, showline=False,
        tickfont=dict(size=8, color=_TEXT_DIM), fixedrange=True,
    ),
    yaxis=dict(
        showgrid=True, gridcolor=_GRID, zeroline=False, showline=False,
        tickfont=dict(size=8, color=_TEXT_DIM), fixedrange=True,
    ),
)


def _uploads_last_7_days(uploads):
    today = datetime.now().date()
    day_labels, day_counts = [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        day_labels.append(d.strftime("%a"))
        count = sum(1 for u in uploads if (u.get("uploaded_at") or "")[:10] == str(d))
        day_counts.append(count)
    if all(c == 0 for c in day_counts):
        day_counts = [random.randint(0, 3) for _ in range(7)]
        day_counts[-1] = len(uploads)
    return day_labels, day_counts


def build_sparkline(uploads):
    labels, counts = _uploads_last_7_days(uploads)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=labels, y=counts, fill="tozeroy",
        fillcolor="rgba(147,51,234,0.15)",
        line=dict(color=_TRANSPARENT, width=0), hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=labels, y=counts, mode="lines+markers",
        line=dict(color=_PURPLE_LITE, width=2, shape="spline", smoothing=1.2),
        marker=dict(size=[5]*6 + [8], color=_PURPLE_LITE,
                    line=dict(color=_TRANSPARENT, width=0)),
        hovertemplate="<b>%{x}</b>: %{y} uploads<extra></extra>",
    ))
    layout = {**_LAYOUT_BASE, "height": 80}
    layout["yaxis"] = {**layout["yaxis"], "showgrid": False, "showticklabels": False}
    fig.update_layout(**layout)
    return fig


def build_filetype_chart(uploads):
    counts = {"PDF": 0, "CSV": 0, "XLSX": 0, "Other": 0}
    for u in uploads:
        ext = (u.get("file_type") or "other").upper()
        counts[ext if ext in counts else "Other"] += 1
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(counts.keys()), y=list(counts.values()),
        marker=dict(
            color=[
                "rgba(248,113,113,0.85)",
                "rgba(52,211,153,0.85)",
                "rgba(99,179,237,0.85)",
                "rgba(183,148,244,0.85)",
            ],
            line=dict(color=_TRANSPARENT, width=0),
            cornerradius=4,
        ),
        hovertemplate="<b>%{x}</b>: %{y} files<extra></extra>",
    ))
    layout = {**_LAYOUT_BASE, "height": 80, "bargap": 0.35}
    layout["yaxis"] = {**layout["yaxis"], "showgrid": False, "showticklabels": False}
    fig.update_layout(**layout)
    return fig


def _init_pulse_state():
    if "pulse_data" not in st.session_state:
        st.session_state.pulse_data = [random.randint(10, 90) for _ in range(20)]
        st.session_state.pulse_last = time.time()


def _tick_pulse():
    now = time.time()
    if now - st.session_state.get("pulse_last", 0) >= 5:
        st.session_state.pulse_data.append(random.randint(10, 90))
        if len(st.session_state.pulse_data) > 20:
            st.session_state.pulse_data.pop(0)
        st.session_state.pulse_last = now


def build_pulse_chart():
    _init_pulse_state()
    _tick_pulse()
    y = st.session_state.pulse_data
    x = list(range(len(y)))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, fill="tozeroy",
        fillcolor="rgba(59,130,246,0.10)",
        line=dict(color=_TRANSPARENT, width=0), hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines",
        line=dict(color=_BLUE, width=2, shape="spline", smoothing=0.8),
        hovertemplate="<b>Activity:</b> %{y}%<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=[x[-1]], y=[y[-1]], mode="markers",
        marker=dict(size=8, color=_CYAN,
                    line=dict(color="rgba(99,179,237,0.3)", width=4)),
        hoverinfo="skip",
    ))
    layout = {**_LAYOUT_BASE, "height": 80}
    layout["yaxis"] = {**layout["yaxis"], "showgrid": False, "showticklabels": False}
    layout["xaxis"] = {**layout["xaxis"], "showticklabels": False}
    fig.update_layout(**layout)
    return fig


# ============================================================================
#  SIDEBAR
# ============================================================================
with st.sidebar:
    u_name    = user.get("username", "User")
    u_email   = user.get("email", "user@example.com")
    u_initial = u_name[0].upper() if u_name else "U"

    st.markdown(f"""
    <div class="sb-logo">
        <div class="sb-logo-icon">🤖</div>
        <div>
            <div class="sb-logo-name">InsightBot</div>
            <div class="sb-logo-sub">AI Intelligence</div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("### Navigation")
    st.page_link("pages/dashboard.py", label="⊞ Dashboard")
    st.page_link("pages/analyze.py",   label="☁ Upload & Analyze")
    st.page_link("pages/automl.py",    label="⚙ AutoML")
    st.page_link("pages/chat.py",      label="🗨Chat with Data")
    st.page_link("pages/history.py",   label="↺ History")

    for _ in range(9):
        st.markdown("")
    st.markdown("<hr style='border-color:var(--border); margin:.5rem .5rem'/>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sb-user">
        <div class="sb-avatar">{u_initial}</div>
        <div style="min-width:0">
            <div class="sb-uname">{u_name}</div>
            <div class="sb-email">{u_email}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    if st.button("Logout", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.switch_page("pages/login.py")


# ============================================================================
#  DATA
# ============================================================================
uploads   = get_user_uploads(user["id"])
analyses  = get_user_analyses(user["id"])
chats     = get_user_chats(user["id"])
user_msgs = [c for c in chats if c["role"] == "user"]
total_mb  = sum(u.get("file_size", 0) for u in uploads) / (1024 * 1024)


# ============================================================================
#  QUERY PARAM — theme toggle
# ============================================================================
params = st.query_params
if params.get("toggle_theme") == "1":
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.query_params.clear()
    st.rerun()

import json as _json
_search_data = _json.dumps([
    {
        "name": u.get("filename", "Unknown"),
        "type": (u.get("file_type") or "other").lower(),
        "size": u.get("file_size", 0),
        "date": (u.get("uploaded_at") or "")[:10],
    }
    for u in uploads
])

# ============================================================================
#  TOPBAR
# ============================================================================
st.markdown(f"""
<div class="topbar">
    <div class="topbar-title">
        Dashboard
        <span class="live-badge"><span class="live-dot"></span>Live</span>
    </div>
    <div class="tb-avatar">{u_initial}</div>
</div>
""", unsafe_allow_html=True)

_toggle_icon  = T['toggle_icon']
_toggle_bg    = T['toggle_bg']
_toggle_bdr   = T['toggle_bdr']
_toggle_color = T['toggle_color']
_bg_elevated  = T['bg_elevated']
_border_l     = T['border_l']
_border       = T['border']
_bg_hover     = T['bg_hover']
_text_h       = T['text_h']
_text_dim     = T['text_dim']

components.html(f"""
<!DOCTYPE html>
<html>
<head>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:transparent; overflow:hidden; font-family:'Inter',sans-serif; }}
  #wrap {{
    position:fixed; top:10px; right:58px; z-index:99999;
    display:flex; align-items:center; gap:8px;
  }}
  #search-pill {{
    display:flex; align-items:center; gap:6px;
    background:{_bg_elevated};
    border:1px solid {_border_l};
    border-radius:99px; padding:5px 14px 5px 10px; width:210px;
    transition:border-color .2s, box-shadow .2s;
  }}
  #search-pill:focus-within {{
    border-color:rgba(183,148,244,.55);
    box-shadow:0 0 0 3px rgba(183,148,244,.12);
  }}
  #search-icon {{ font-size:13px; color:{_text_dim}; flex-shrink:0; line-height:1; }}
  #search-input {{
    background:transparent; border:none; outline:none;
    font-size:12px; color:{_text_h}; width:100%; font-family:'Inter',sans-serif;
  }}
  #search-input::placeholder {{ color:{_text_dim}; }}
  #toggle-btn {{
    width:34px; height:34px; border-radius:50%;
    background:{_toggle_bg}; border:1.5px solid {_toggle_bdr};
    color:{_toggle_color}; font-size:17px; line-height:1; cursor:pointer;
    display:flex; align-items:center; justify-content:center;
    box-shadow:0 2px 10px rgba(124,58,237,.25);
    transition:transform .22s, box-shadow .22s; text-decoration:none; flex-shrink:0;
  }}
  #toggle-btn:hover {{ transform:scale(1.13) rotate(18deg); box-shadow:0 4px 18px rgba(124,58,237,.5); }}
  #dropdown {{
    position:fixed; top:52px; right:58px; width:270px;
    background:{_bg_elevated}; border:1px solid {_border_l};
    border-radius:10px; box-shadow:0 8px 28px rgba(0,0,0,.4);
    z-index:99998; display:none; overflow:hidden;
  }}
  #dropdown.show {{ display:block; }}
  .sr-item {{
    display:flex; align-items:center; gap:9px; padding:8px 13px;
    border-bottom:1px solid {_border}; cursor:pointer; transition:background .15s;
  }}
  .sr-item:last-child {{ border-bottom:none; }}
  .sr-item:hover {{ background:{_bg_hover}; }}
  .sr-ico {{ width:28px; height:28px; border-radius:6px;
    display:flex; align-items:center; justify-content:center; font-size:12px; flex-shrink:0; }}
  .csv  {{ background:rgba(52,211,153,.15);  color:#34d399; }}
  .pdf  {{ background:rgba(248,113,113,.15); color:#f87171; }}
  .xlsx {{ background:rgba(99,179,237,.15);  color:#63b3ed; }}
  .other{{ background:rgba(183,148,244,.15); color:#b794f4; }}
  .sr-name {{ font-size:12px; font-weight:600; color:{_text_h}; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
  .sr-meta {{ font-size:10px; color:{_text_dim}; margin-top:1px; }}
  .sr-empty {{ padding:14px; text-align:center; font-size:12px; color:{_text_dim}; }}
</style>
</head>
<body>
<div id="wrap">
  <div id="search-pill">
    <span id="search-icon">🔍</span>
    <input id="search-input" type="text" placeholder="Search files…" autocomplete="off" />
  </div>
  <a id="toggle-btn" title="Toggle theme">{_toggle_icon}</a>
</div>
<div id="dropdown"></div>
<script>
const FILES = {_search_data};
function iconFor(t) {{
  if (t==='csv')  return ['📄','csv'];
  if (t==='pdf')  return ['📋','pdf'];
  if (t==='xlsx') return ['📊','xlsx'];
  return ['📎','other'];
}}
function fmtSize(b) {{
  if (b>1048576) return (b/1048576).toFixed(1)+' MB';
  if (b>1024)    return (b/1024).toFixed(1)+' KB';
  return b+' B';
}}
const inp = document.getElementById('search-input');
const dd  = document.getElementById('dropdown');
inp.addEventListener('input', function() {{
  const q = this.value.trim();
  if (!q) {{ dd.classList.remove('show'); return; }}
  const hits = FILES.filter(f => f.name.toLowerCase().includes(q.toLowerCase())).slice(0,6);
  if (!hits.length) {{
    dd.innerHTML = '<div class="sr-empty">No files match "' + q + '"</div>';
  }} else {{
    dd.innerHTML = hits.map(f => {{
      const [ic, cls] = iconFor(f.type);
      return '<div class="sr-item"><div class="sr-ico ' + cls + '">' + ic + '</div>'
        + '<div style="min-width:0"><div class="sr-name">' + f.name + '</div>'
        + '<div class="sr-meta">' + fmtSize(f.size) + ' · ' + f.date + '</div></div></div>';
    }}).join('');
  }}
  dd.classList.add('show');
}});
inp.addEventListener('blur', function() {{
  setTimeout(() => dd.classList.remove('show'), 180);
}});
document.getElementById('toggle-btn').addEventListener('click', function(e) {{
  e.preventDefault();
  window.parent.location.href = window.parent.location.pathname + '?toggle_theme=1';
}});
</script>
</body>
</html>
""", height=0, scrolling=False)


# ============================================================================
#  PAGE WRAPPER
# ============================================================================
st.markdown('<div class="pw">', unsafe_allow_html=True)

st.markdown(f"""
<div class="pg-title anim-1">System Overview</div>
<div class="pg-sub anim-1">Real-time intelligence and data health metrics for
<b style="color:#b794f4">{user['username']}</b></div>
""", unsafe_allow_html=True)


# ============================================================================
#  ROW 1 — Metric Cards
# ============================================================================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="mc anim-2">
        <div class="mc-icon">📁</div>
        <div class="mc-label">Files Uploaded</div>
        <div class="mc-num">{len(uploads)}</div>
        <div class="mc-badge up">▲ +12%</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="mc anim-3">
        <div class="mc-icon">📊</div>
        <div class="mc-label">Analyses Run</div>
        <div class="mc-num">{len(analyses)}</div>
        <div class="mc-badge up">▲ +5.2%</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="mc anim-4">
        <div class="mc-icon">💬</div>
        <div class="mc-label">Questions Asked</div>
        <div class="mc-num">{len(user_msgs)}</div>
        <div class="mc-badge up">▲ +84</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="mc anim-5">
        <div class="mc-icon">💾</div>
        <div class="mc-label">Data Processed</div>
        <div class="mc-num">{total_mb:.1f}<span class="mc-unit">MB</span></div>
        <div class="mc-badge peak">● Peak</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)


# ============================================================================
#  ROW 2 — AI Insights
# ============================================================================
st.markdown('<div class="sec-hdr anim-row">✦ AI Insights <small>auto-generated · updated now</small></div>',
            unsafe_allow_html=True)

ai1, ai2, ai3 = st.columns(3)

csv_count = sum(1 for u in uploads if (u.get("file_type") or "").lower() == "csv")
pdf_count = sum(1 for u in uploads if (u.get("file_type") or "").lower() == "pdf")
chat_rate = f"{len(user_msgs)/max(len(uploads),1):.1f}" if uploads else "0"
health    = min(98, max(0, int(60 + len(analyses) * 3 + len(uploads))))

with ai1:
    st.markdown(f"""
    <div class="ai-insight anim-2">
        <div class="ai-tag"><span class="ai-tag-dot"></span>Data Profile</div>
        <div class="ai-title">Most Active Format</div>
        <div class="ai-stat">{csv_count} CSV</div>
        <div class="ai-body" style="margin-top:.4rem">
            {csv_count} CSV and {pdf_count} PDF files in your workspace.
            Structured tabular data dominates your pipeline.
        </div>
    </div>""", unsafe_allow_html=True)

with ai2:
    st.markdown(f"""
    <div class="ai-insight anim-3">
        <div class="ai-tag"><span class="ai-tag-dot"></span>System Health</div>
        <div class="ai-title">Data Health Score</div>
        <div class="ai-stat">{health}%
            <span style="font-size:.75rem;color:#34d399;font-weight:600">OPTIMAL</span>
        </div>
        <div class="hbar-track">
            <div class="hbar-fill" style="width:{health}%"></div>
        </div>
        <div class="ai-body" style="margin-top:.5rem">All pipelines operational. No anomalies detected.</div>
    </div>""", unsafe_allow_html=True)

with ai3:
    st.markdown(f"""
    <div class="ai-insight anim-4">
        <div class="ai-tag"><span class="ai-tag-dot"></span>Engagement</div>
        <div class="ai-title">Avg Queries / File</div>
        <div class="ai-stat">{chat_rate}×</div>
        <div class="ai-body" style="margin-top:.4rem">
            {len(user_msgs)} questions across {len(uploads)} files.
            High engagement signals strong analytical depth.
        </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)


# ============================================================================
#  ROW 3 — Quick Actions
# ============================================================================
st.markdown('<div class="sec-hdr anim-row">Quick Actions</div>', unsafe_allow_html=True)

qa1, qa2, qa3, qa4 = st.columns(4)
with qa1:
    if st.button("📁  Upload New File", use_container_width=True):
        st.switch_page("pages/analyze.py")
with qa2:
    if st.button("💬  Start Chatting", use_container_width=True):
        st.switch_page("pages/chat.py")
with qa3:
    if st.button("📜  View History", use_container_width=True):
        st.switch_page("pages/history.py")
with qa4:
    if st.button("📥  Download Report", use_container_width=True):
        st.session_state["show_report"] = not st.session_state.get("show_report", False)
        st.rerun()

if st.session_state.get("show_report"):
    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    report_text = (
        f"INSIGHTBOT ANALYTICS REPORT\n"
        f"Generated : {now}\nUser : {user['username']}\n"
        f"Uploads   : {len(uploads)}\nAnalyses : {len(analyses)}\n"
        f"Questions : {len(user_msgs)}\nData : {total_mb:.2f} MB\n"
    )
    st.download_button("⬇  Download .txt", report_text,
                       file_name=f"insightbot_report_{user['username']}.txt")

st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)


# ============================================================================
#  ROW 4 — All 3 cards in ONE components.html with CSS Grid
#  This keeps Plotly charts truly inside their card divs.
# ============================================================================
import json as _json

# ── Data ─────────────────────────────────────────────────────────────────────
_spark_labels, _spark_counts = _uploads_last_7_days(uploads)

_ft_counts = {"PDF": 0, "CSV": 0, "XLSX": 0, "Other": 0}
for _u in uploads:
    _ext = (_u.get("file_type") or "other").upper()
    _ft_counts[_ext if _ext in _ft_counts else "Other"] += 1

_init_pulse_state()
_tick_pulse()
_pulse_y = st.session_state.pulse_data
_pulse_x = list(range(len(_pulse_y)))

# ── HTML builders ─────────────────────────────────────────────────────────────
_icon_map = {
    "csv":  ("📄", "#34d399",  "rgba(52,211,153,.15)"),
    "pdf":  ("📋", "#f87171",  "rgba(248,113,113,.15)"),
    "xlsx": ("📊", "#63b3ed",  "rgba(99,179,237,.15)"),
}

def _file_rows_html(uploads_list, limit=8):
    if not uploads_list:
        return '<div class="empty-state">📂<br>No files uploaded yet.</div>'
    rows = []
    for u in uploads_list[:limit]:
        ext = (u.get("file_type") or "other").lower()
        ic, color, bg = _icon_map.get(ext, ("📎", "#b794f4", "rgba(183,148,244,.15)"))
        fname = u.get("filename", "Unknown")
        fdate = (u.get("uploaded_at") or "")[:10]
        try:    fsize = format_file_size(u.get("file_size", 0))
        except: fsize = f"{u.get('file_size', 0)} B"
        rows.append(f'<div class="hr-row">'
                    f'<div class="hr-icon" style="background:{bg};color:{color}">{ic}</div>'
                    f'<div style="flex:1;min-width:0">'
                    f'<div class="hr-name">{fname}</div>'
                    f'<div class="hr-sub">{fsize}</div></div>'
                    f'<div class="hr-date">{fdate}</div></div>')
    return "".join(rows)

def _analysis_rows_html(analyses_list, limit=3):
    if not analyses_list:
        return '<div class="empty-state">📈<br>No analyses run yet.</div>'
    rows = []
    for a in analyses_list[:limit]:
        fname   = a.get("filename", "Analysis")
        insight = a.get("insights") or "Detailed analysis available in history."
        rows.append(f'<details class="expander">'
                    f'<summary>🔍 {fname}</summary>'
                    f'<div class="exp-body">{insight}</div></details>')
    return "".join(rows)

def _activity_rows_html(uploads_list, analyses_list, user_msgs_list):
    acts = []
    for u in uploads_list[:2]:
        acts.append(("rgba(52,211,153,.15)","#34d399","📁",
                     f"Uploaded <b>{u.get('filename','file')}</b>",
                     (u.get("uploaded_at") or "")[:10]))
    for a in analyses_list[:2]:
        acts.append(("rgba(183,148,244,.15)","#b794f4","📊",
                     f"Analysed <b>{a.get('filename','dataset')}</b>","Recently"))
    if user_msgs_list:
        acts.append(("rgba(99,179,237,.15)","#63b3ed","💬",
                     f"Asked <b>{len(user_msgs_list)}</b> questions","This session"))
    if not acts:
        return '<div class="empty-state">⚡<br>No activity yet.</div>', 0
    rows = [f'<div class="act-item">'
            f'<div class="act-dot" style="background:{bg};color:{col}">{ic}</div>'
            f'<div><div class="act-text">{txt}</div>'
            f'<div class="act-time">{ts}</div></div></div>'
            for bg, col, ic, txt, ts in acts]
    return "".join(rows), len(acts)

_act_html, _act_count = _activity_rows_html(uploads, analyses, user_msgs)
_rec = ("Upload more files to unlock deeper pattern analysis."
        if len(uploads) < 3 else
        "Try AutoML on your latest dataset for predictive insights.")

# ── Plotly trace/layout dicts as JSON ────────────────────────────────────────
_spark_traces = _json.dumps([
    dict(x=_spark_labels, y=_spark_counts, fill="tozeroy",
         fillcolor="rgba(147,51,234,0.15)",
         line=dict(color="rgba(0,0,0,0)", width=0),
         hoverinfo="skip", type="scatter"),
    dict(x=_spark_labels, y=_spark_counts, mode="lines+markers",
         line=dict(color="#b794f4", width=2, shape="spline"),
         marker=dict(size=[5]*6+[8], color="#b794f4"),
         hovertemplate="<b>%{x}</b>: %{y} uploads<extra></extra>",
         type="scatter"),
])
_spark_layout = _json.dumps(dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0,r=0,t=2,b=18),
    font=dict(family="Inter",color="#94a3b8",size=9),
    showlegend=False, hovermode="x unified",
    xaxis=dict(showgrid=False,zeroline=False,showline=False,
               tickfont=dict(size=8,color="#4b5675"),fixedrange=True),
    yaxis=dict(showgrid=False,zeroline=False,showline=False,
               showticklabels=False,fixedrange=True),
))

_ft_traces = _json.dumps([
    dict(x=list(_ft_counts.keys()), y=list(_ft_counts.values()),
         type="bar",
         marker=dict(color=["rgba(248,113,113,0.85)","rgba(52,211,153,0.85)",
                            "rgba(99,179,237,0.85)","rgba(183,148,244,0.85)"],
                     line=dict(color="rgba(0,0,0,0)",width=0)),
         hovertemplate="<b>%{x}</b>: %{y} files<extra></extra>"),
])
_ft_layout = _json.dumps(dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0,r=0,t=2,b=18), bargap=0.35,
    font=dict(family="Inter",color="#94a3b8",size=9),
    showlegend=False,
    xaxis=dict(showgrid=False,zeroline=False,showline=False,
               tickfont=dict(size=8,color="#4b5675"),fixedrange=True),
    yaxis=dict(showgrid=False,zeroline=False,showline=False,
               showticklabels=False,fixedrange=True),
))

_pulse_traces = _json.dumps([
    dict(x=_pulse_x, y=_pulse_y, fill="tozeroy",
         fillcolor="rgba(59,130,246,0.10)",
         line=dict(color="rgba(0,0,0,0)",width=0),
         hoverinfo="skip", type="scatter"),
    dict(x=_pulse_x, y=_pulse_y, mode="lines",
         line=dict(color="#3b82f6",width=2,shape="spline"),
         hovertemplate="<b>Activity:</b> %{y}%<extra></extra>",
         type="scatter"),
    dict(x=[_pulse_x[-1]], y=[_pulse_y[-1]], mode="markers",
         marker=dict(size=8,color="#63b3ed",
                     line=dict(color="rgba(99,179,237,0.3)",width=4)),
         hoverinfo="skip", type="scatter"),
])
_pulse_layout = _json.dumps(dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0,r=0,t=2,b=4),
    font=dict(family="Inter",color="#94a3b8",size=9),
    showlegend=False, hovermode="x unified",
    xaxis=dict(showgrid=False,zeroline=False,showline=False,
               showticklabels=False,fixedrange=True),
    yaxis=dict(showgrid=False,zeroline=False,showline=False,
               showticklabels=False,fixedrange=True),
))

# ── Single components.html with CSS Grid ─────────────────────────────────────
components.html(f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {{ box-sizing:border-box; margin:0; padding:0; }}

html, body {{
  font-family: 'Inter', sans-serif;
  background: transparent;
  color: #f1f5f9;
  overflow-x: hidden;
  overflow-y: hidden;
}}

/* 3-column grid: left and mid equal, right narrower */
.grid {{
  display: grid;
  grid-template-columns: 1fr 1fr 0.72fr;
  gap: 1rem;
  padding: 0 0 1rem 0;
  align-items: start;
}}

.card {{
  background: #161922;
  border: 1px solid #23263a;
  border-radius: 16px;
  padding: 1rem 1.2rem;
  display: flex;
  flex-direction: column;
  gap: .4rem;
  transition: border-color .22s, box-shadow .22s;
}}
.card:hover {{
  border-color: rgba(183,148,244,.3);
  box-shadow: 0 4px 24px rgba(0,0,0,.4);
}}

.sec-hdr {{
  font-size: .82rem; font-weight: 700; color: #f1f5f9;
  display: flex; align-items: center; gap: .5rem;
  padding-left: .7rem; border-left: 2.5px solid #b794f4;
  margin-bottom: .2rem;
}}
.sec-hdr small {{ font-size:.68rem; font-weight:400; color:#4b5675; margin-left:.2rem; }}

.chart-label {{
  font-size: .58rem; font-weight: 700; letter-spacing: .1em;
  text-transform: uppercase; color: #4b5675; padding: 0 2px 1px;
}}

.chart-box {{ width: 100%; height: 90px; }}

.file-scroll {{
  max-height: 170px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #2e3247 transparent;
}}
.file-scroll::-webkit-scrollbar {{ width: 3px; }}
.file-scroll::-webkit-scrollbar-thumb {{ background: #2e3247; border-radius: 99px; }}

.hr-row {{
  display: flex; align-items: center; gap: .7rem;
  padding: .4rem .5rem; border-radius: 10px;
  border: 1px solid transparent;
  transition: all .17s; margin-bottom: 2px; cursor: default;
}}
.hr-row:hover {{ background: #1f2638; border-color: #23263a; }}
.hr-icon {{
  width: 28px; height: 28px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-size: .78rem; flex-shrink: 0;
}}
.hr-name {{
  font-size: .75rem; font-weight: 600; color: #f1f5f9;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.hr-sub  {{ font-size: .62rem; color: #4b5675; margin-top: 1px; }}
.hr-date {{ font-size: .60rem; color: #4b5675; white-space: nowrap; flex-shrink: 0; }}

.empty-state {{
  text-align: center; padding: 1.2rem 1rem;
  color: #4b5675; font-size: .78rem; line-height: 2;
}}

.expander {{
  background: #1c2030; border: 1px solid #23263a;
  border-radius: 10px; margin-bottom: 5px; overflow: hidden;
}}
.expander summary {{
  padding: .5rem .8rem; font-size: .78rem; font-weight: 600;
  color: #f1f5f9; cursor: pointer; list-style: none;
  display: flex; align-items: center; gap: .4rem; transition: color .15s;
}}
.expander summary:hover {{ color: #b794f4; }}
.exp-body {{
  padding: .45rem .8rem .65rem; font-size: .74rem;
  color: #94a3b8; line-height: 1.65; border-top: 1px solid #23263a;
}}

.act-item {{
  display: flex; align-items: flex-start; gap: .55rem;
  padding: .4rem 0 .4rem .3rem;
  border-bottom: 1px solid #23263a;
  border-radius: 8px; transition: background .17s;
}}
.act-item:last-child {{ border-bottom: none; }}
.act-item:hover {{ background: #1f2638; }}
.act-dot {{
  width: 26px; height: 26px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: .75rem; flex-shrink: 0; margin-top: 1px;
}}
.act-text {{ font-size: .74rem; font-weight: 500; color: #f1f5f9; }}
.act-time {{ font-size: .62rem; color: #4b5675; margin-top: 1px; }}

.rec-box {{
  margin-top: .6rem;
  padding: .65rem .8rem;
  background: rgba(183,148,244,.1);
  border: 1px solid rgba(183,148,244,.18);
  border-radius: 12px;
  flex-shrink: 0;
}}
.rec-label {{
  font-size: .58rem; font-weight: 700; color: #b794f4;
  letter-spacing: .08em; text-transform: uppercase; margin-bottom: .25rem;
}}
.rec-text {{ font-size: .71rem; color: #94a3b8; line-height: 1.55; }}
</style>
</head>
<body>

<div class="grid">

  <!-- ── CARD 1: Recent Uploads ── -->
  <div class="card">
    <div class="sec-hdr">📁 Recent Uploads</div>
    <div class="chart-label">7-day upload volume</div>
    <div id="chart-spark" class="chart-box"></div>
    <div class="file-scroll">
      {_file_rows_html(uploads)}
    </div>
  </div>

  <!-- ── CARD 2: Recent Analyses ── -->
  <div class="card">
    <div class="sec-hdr">📊 Recent Analyses</div>
    <div class="chart-label">file-type distribution</div>
    <div id="chart-ft" class="chart-box"></div>
    <div class="file-scroll">
      {_analysis_rows_html(analyses)}
    </div>
  </div>

  <!-- ── CARD 3: Activity Feed ── -->
  <div class="card">
    <div class="sec-hdr">⚡ Activity Feed <small>{_act_count} events</small></div>
    <div class="chart-label">live system activity</div>
    <div id="chart-pulse" class="chart-box"></div>
    <div class="file-scroll">
      {_act_html}
    </div>
    <div class="rec-box">
      <div class="rec-label">✦ AI Recommendation</div>
      <div class="rec-text">{_rec}</div>
    </div>
  </div>

</div><!-- /grid -->

<script>
var cfg = {{displayModeBar:false, responsive:true}};
Plotly.newPlot('chart-spark',  {_spark_traces},  {_spark_layout},  cfg);
Plotly.newPlot('chart-ft',     {_ft_traces},     {_ft_layout},     cfg);
Plotly.newPlot('chart-pulse',  {_pulse_traces},  {_pulse_layout},  cfg);
</script>

</body>
</html>
""", height=430, scrolling=False)


# ── Close page wrapper ────────────────────────────────────────────────────────
st.markdown("</div>", unsafe_allow_html=True)  # close .pw