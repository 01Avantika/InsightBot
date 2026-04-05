import streamlit as st
import sys, os, random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

st.set_page_config(
    page_title="InsightBot - AI-Powered Data Intelligence Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# ─────────────────────────────────────────────────────────────────────────────
# THEME TOGGLE — must be FIRST Streamlit widget rendered
# ─────────────────────────────────────────────────────────────────────────────
def render_toggle():
    dm = st.session_state.dark_mode
    label = "☀" if dm else "☽"
    col1, col2, col3 = st.columns([8, 0.5, 0.5])
    with col3:
        if st.button(label, key="theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────
def load_css():
    dm = st.session_state.dark_mode

    bg        = '#0d1117' if dm else '#ffffff'
    bg2       = '#161b22' if dm else '#f5f3ff'
    text      = '#f0f6fc' if dm else '#0f172a'
    text2     = '#8b949e' if dm else '#64748b'
    purple    = '#a855f7' if dm else '#9333ea'
    purple2   = '#c084fc' if dm else '#7c3aed'
    border    = '#30363d' if dm else '#e9d5ff'
    card      = '#161b22' if dm else '#ffffff'
    navbar_bg = 'rgba(13,17,23,0.96)' if dm else 'rgba(255,255,255,0.96)'

    ib   = 'rgba(168,85,247,0.15)' if dm else 'rgba(147,51,234,0.08)'
    ibh  = 'rgba(168,85,247,0.30)' if dm else 'rgba(147,51,234,0.18)'
    ic   = '#c084fc'               if dm else '#7c3aed'
    ishadow = 'rgba(168,85,247,0.30)' if dm else 'rgba(147,51,234,0.18)'
    gc   = 'rgba(168,85,247,0.07)' if dm else 'rgba(147,51,234,0.05)'
    ts   = '0 2px 24px rgba(0,0,0,0.5)' if dm else '0 2px 12px rgba(0,0,0,0.07)'

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

* {{ font-family:'Inter',-apple-system,BlinkMacSystemFont,sans-serif; box-sizing:border-box; margin:0; padding:0; }}
.main .block-container {{ padding-top:0!important; padding-bottom:0!important; max-width:100%!important; }}
.stApp {{ background:{bg}!important; }}
#MainMenu, footer, header {{ visibility:hidden; }}

/* ══════════════════════════════════════════════════════════
   HIDE ALL STREAMLIT CHROME — keep only our toggle button
══════════════════════════════════════════════════════════ */
/* Push the very first st.columns block (our toggle row) fixed into navbar */
section[data-testid="stMain"] > div > div[data-testid="stVerticalBlock"] > div:nth-child(1) > div[data-testid="stHorizontalBlock"] {{
    position: fixed !important;
    top: 12px !important;
    right: 24px !important;
    z-index: 2000 !important;
    width: auto !important;
    background: transparent !important;
    gap: 0 !important;
    pointer-events: all;
}}
/* Hide first two spacer columns, show only last (button) column */
section[data-testid="stMain"] > div > div[data-testid="stVerticalBlock"] > div:nth-child(1) > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1),
section[data-testid="stMain"] > div > div[data-testid="stVerticalBlock"] > div:nth-child(1) > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) {{
    display: none !important;
}}
section[data-testid="stMain"] > div > div[data-testid="stVerticalBlock"] > div:nth-child(1) > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(3) {{
    pointer-events: all !important;
    display: flex !important;
    justify-content: flex-end !important;
}}

/* ── Toggle button style ── */
.stButton > button {{
    background: {ib} !important;
    border: 1px solid rgba(168,85,247,0.40) !important;
    border-radius: 10px !important;
    width: 40px !important;
    height: 40px !important;
    padding: 0 !important;
    font-size: 1.1rem !important;
    line-height: 1 !important;
    color: {text} !important;
    box-shadow: 0 2px 14px {ishadow} !important;
    transition: all 0.25s !important;
    cursor: pointer !important;
}}
.stButton > button:hover {{
    background: {ibh} !important;
    transform: translateY(-2px) scale(1.07) !important;
    box-shadow: 0 6px 20px {ishadow} !important;
    border-color: rgba(168,85,247,0.65) !important;
}}
.stButton > button p {{
    font-size: 1.1rem !important;
    color: {text} !important;
    margin: 0 !important;
    line-height: 1 !important;
}}

/* ══════════════════════════════════════════════════════════
   NAVBAR (HTML-only, no Streamlit widgets inside)
══════════════════════════════════════════════════════════ */
.navbar {{
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 64px;
    z-index: 1000;
    background: {navbar_bg};
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    border-bottom: 1px solid {border};
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 5%;
}}
.navbar-logo {{
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a855f7, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    flex-shrink: 0;
}}
.navbar-links {{
    display: flex;
    gap: 3rem;
    align-items: center;
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
}}
.navbar-link {{
    color: {text} !important;
    text-decoration: none !important;
    font-weight: 700;
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    transition: color 0.2s;
    white-space: nowrap;
}}
.navbar-link:hover {{ color: #a855f7 !important; }}
/* right spacer so links stay truly centered */
.navbar-right {{ flex-shrink: 0; width: 40px; }}

/* ══════════════════════════════════════════════════════════
   HERO
══════════════════════════════════════════════════════════ */
.hero-wrapper {{
    position: relative;
    width: 100%;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    background: {bg};
    padding: 80px 2rem 4rem;
}}
/* subtle grid */
.hero-wrapper::before {{
    content: '';
    position: absolute; inset: 0;
    background-image:
        linear-gradient({gc} 1px, transparent 1px),
        linear-gradient(90deg, {gc} 1px, transparent 1px);
    background-size: 64px 64px;
    mask-image: radial-gradient(ellipse 85% 70% at 50% 45%, black, transparent);
    -webkit-mask-image: radial-gradient(ellipse 85% 70% at 50% 45%, black, transparent);
    pointer-events: none;
    z-index: 0;
}}
/* center glow */
.hero-glow {{
    position: absolute;
    width: 720px; height: 720px;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    background: radial-gradient(circle, rgba(168,85,247,0.13) 0%, transparent 68%);
    animation: glowPulse 6s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}}
@keyframes glowPulse {{
    0%,100% {{ opacity:0.6; transform:translate(-50%,-50%) scale(1); }}
    50%      {{ opacity:1.0; transform:translate(-50%,-50%) scale(1.18); }}
}}
.hero-orb-l {{
    position: absolute;
    width: 500px; height: 500px;
    top: -100px; left: -130px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(168,85,247,0.20), transparent 70%);
    filter: blur(55px);
    animation: orbL 16s ease-in-out infinite;
    pointer-events: none; z-index: 0;
}}
.hero-orb-r {{
    position: absolute;
    width: 420px; height: 420px;
    bottom: -60px; right: -90px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(99,102,241,0.18), transparent 70%);
    filter: blur(55px);
    animation: orbR 19s ease-in-out infinite;
    pointer-events: none; z-index: 0;
}}
@keyframes orbL {{ 0%,100%{{transform:translate(0,0)}} 50%{{transform:translate(70px,90px)}} }}
@keyframes orbR {{ 0%,100%{{transform:translate(0,0)}} 50%{{transform:translate(-70px,-65px)}} }}

/* floating dots */
.dot {{
    position: absolute;
    border-radius: 50%;
    pointer-events: none;
    z-index: 1;
    opacity: 0;
    animation: dotUp linear infinite;
}}
@keyframes dotUp {{
    0%   {{ opacity:0;   transform:translateY(0) scale(0.4); }}
    8%   {{ opacity:0.9; }}
    88%  {{ opacity:0.6; }}
    100% {{ opacity:0;   transform:translateY(-500px) scale(1.1); }}
}}

/* hero content */
.hero-content {{
    position: relative;
    z-index: 10;
    text-align: center;
    max-width: 860px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    align-items: center;
}}

/* ── BADGE — simple glowing pill, NO rotation, NO conic border ── */
.hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.45rem 1.3rem;
    border-radius: 9999px;
    border: 1.5px solid rgba(168,85,247,0.45);
    background: rgba(168,85,247,0.10);
    backdrop-filter: blur(10px);
    margin-bottom: 2rem;
    animation: badgePulse 3s ease-in-out infinite;
}}
@keyframes badgePulse {{
    0%,100% {{ box-shadow: 0 0 10px 0 rgba(168,85,247,0.4); }}
    50%      {{ box-shadow: 0 0 24px 5px rgba(168,85,247,0.6); }}
}}
.badge-text {{
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {purple2};
}}

/* ── hero text ── */
.hero-title {{
    font-size: clamp(2.6rem, 5.5vw, 4.8rem);
    font-weight: 900;
    line-height: 1.15;
    color: {text} !important;
    margin-bottom: 1.6rem;
    text-shadow: {ts};
}}
.gradient-text {{
    background: linear-gradient(135deg, #a855f7 0%, #7c3aed 55%, #6366f1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    background-size: 200% 200%;
    animation: gradShift 4s ease infinite;
    display: inline-block;
}}
@keyframes gradShift {{
    0%,100% {{ background-position: 0% 50%; }}
    50%      {{ background-position: 100% 50%; }}
}}
.hero-desc {{
    font-size: 1.15rem;
    color: {text2} !important;
    max-width: 680px;
    margin: 0 auto 2.8rem;
    line-height: 1.85;
}}
.hero-cta {{
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.95rem 2.4rem;
    background: linear-gradient(135deg, #a855f7, #7c3aed);
    color: #ffffff !important;
    border-radius: 0.75rem;
    font-weight: 700;
    font-size: 1.05rem;
    text-decoration: none !important;
    box-shadow: 0 16px 32px -6px rgba(168,85,247,0.55);
    transition: all 0.3s;
    border: none;
    cursor: pointer;
}}
.hero-cta:hover {{
    transform: translateY(-3px) scale(1.04);
    box-shadow: 0 22px 40px -6px rgba(168,85,247,0.65);
    color: #ffffff !important;
    text-decoration: none !important;
}}

/* ══════════════════════════════════════════════════════════
   STATS
══════════════════════════════════════════════════════════ */
.stats-section {{
    background: {card};
    border-top: 1px solid {border};
    border-bottom: 1px solid {border};
    padding: 3.5rem 2rem;
}}
.stat-card {{ text-align:center; padding:1.5rem; transition:transform .3s; }}
.stat-card:hover {{ transform:scale(1.05); }}
.stat-number {{
    font-size: 2.8rem; font-weight: 900;
    background: linear-gradient(135deg, #a855f7, #7c3aed);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; margin-bottom: 0.4rem;
}}
.stat-label {{ font-size:.8rem; font-weight:700; color:{text2}; text-transform:uppercase; letter-spacing:.1em; }}

/* ══════════════════════════════════════════════════════════
   SECTIONS & CARDS
══════════════════════════════════════════════════════════ */
.section     {{ padding:5rem 2rem; background:{bg};  }}
.section-alt {{ padding:5rem 2rem; background:{bg2}; }}

/* hide empty Streamlit column wrappers left by pure-HTML sections */
div[data-testid="stHorizontalBlock"]:empty,
div[data-testid="column"]:empty {{ display:none !important; }}
.section-badge {{
    display:inline-block; padding:.4rem 1rem; border-radius:9999px;
    background:rgba(168,85,247,.12); color:{purple};
    font-weight:700; font-size:.8rem; text-transform:uppercase;
    letter-spacing:.06em; margin-bottom:1.2rem;
}}
.section-title {{
    font-size:clamp(1.8rem,3.5vw,2.8rem); font-weight:800;
    color:{text}!important; margin-bottom:1rem; text-align:center;
}}
.section-sub {{ display:block; text-align:center; color:{text2}!important; max-width:680px; margin:0 auto 3rem; line-height:1.7; width:100%; }}

.card {{
    background:{card}; border:1px solid {border};
    border-radius:1rem; padding:1.8rem; transition:all .3s; height:100%;
}}
.card:hover {{
    border-color:#a855f7;
    box-shadow:0 16px 32px -8px rgba(168,85,247,0.18);
    transform:translateY(-4px);
}}
.card-number  {{ color:{purple2}; font-weight:700; font-size:.8rem; letter-spacing:.1em; margin-bottom:.8rem; }}
.card-title   {{ font-size:1.1rem; font-weight:800; color:{text}!important; margin-bottom:.8rem; }}
.card-desc    {{ color:{text2}!important; line-height:1.7; font-size:.92rem; }}

.workflow-card {{
    background:{card}; border:1px solid {border};
    border-radius:1rem; padding:1.8rem; transition:all .3s; height:100%;
}}
.workflow-card:hover {{
    border-color:#a855f7;
    box-shadow:0 16px 32px -8px rgba(168,85,247,0.18);
    transform:translateY(-6px);
}}
.workflow-badge {{
    display:flex; align-items:center; justify-content:center;
    width:3.5rem; height:3.5rem; border-radius:.875rem;
    background:linear-gradient(135deg,#a855f7,#7c3aed);
    color:#fff; font-weight:900; font-size:1.1rem; margin-bottom:1rem;
    box-shadow:0 8px 20px -4px rgba(168,85,247,0.5); transition:transform .3s;
}}
.workflow-card:hover .workflow-badge {{ transform:scale(1.08) rotate(-3deg); }}

.icon-wrap {{
    display:inline-flex; align-items:center; justify-content:center;
    width:48px; height:48px; border-radius:12px;
    background:{ib}; border:1px solid rgba(168,85,247,.20);
    box-shadow:0 4px 14px {ishadow};
    margin-bottom:1rem; transition:all .25s; flex-shrink:0;
}}
.icon-wrap svg {{
    width:20px; height:20px; stroke:{ic}; fill:none;
    stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round;
}}
.card:hover .icon-wrap, .workflow-card:hover .icon-wrap {{
    background:{ibh}; transform:translateY(-2px);
    box-shadow:0 6px 20px {ishadow};
}}

/* ══════════════════════════════════════════════════════════
   CTA + FOOTER
══════════════════════════════════════════════════════════ */
.cta-section {{
    background:linear-gradient(135deg,#7c3aed,#a855f7,#6366f1);
    padding:6rem 2rem; text-align:center; position:relative; overflow:hidden;
}}
.cta-section::before {{
    content:''; position:absolute; top:-40%; left:20%;
    width:500px; height:500px; background:rgba(255,255,255,.06);
    border-radius:50%; filter:blur(60px);
    animation:ctaP 4s ease-in-out infinite;
}}
@keyframes ctaP {{ 0%,100%{{opacity:.6}} 50%{{opacity:1}} }}
.cta-title   {{ font-size:clamp(1.8rem,4vw,3rem); font-weight:900; color:#fff!important; margin-bottom:1.2rem; position:relative; z-index:1; }}
.cta-desc    {{ font-size:1.15rem; color:rgba(255,255,255,.88)!important; margin-bottom:2rem; position:relative; z-index:1; }}
.cta-btn-w {{
    display:inline-flex; align-items:center; gap:.5rem;
    padding:.9rem 2.2rem; background:#fff; color:#7c3aed!important;
    border-radius:.75rem; font-weight:700; font-size:1.05rem;
    text-decoration:none!important;
    box-shadow:0 20px 40px -8px rgba(0,0,0,.25);
    transition:all .3s; border:none; cursor:pointer; position:relative; z-index:1;
}}
.cta-btn-w:hover {{ transform:translateY(-3px) scale(1.04); color:#7c3aed!important; }}

.custom-footer {{
    background:{card}; border-top:1px solid {border};
    padding:2rem; text-align:center;
}}
.footer-content {{
    display:flex; justify-content:space-between; align-items:center;
    flex-wrap:wrap; gap:1rem; max-width:1200px; margin:0 auto;
}}
.footer-logo {{
    font-size:1.2rem; font-weight:800;
    background:linear-gradient(135deg,#a855f7,#7c3aed);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}}
.footer-text {{ color:{text2}!important; font-size:.85rem; }}

@media(max-width:768px) {{
    .hero-title {{ font-size:2.2rem; }}
    .hero-desc  {{ font-size:1rem; }}
    .section,.section-alt {{ padding:3rem 1rem; }}
    .footer-content {{ flex-direction:column; text-align:center; }}
    .navbar-links {{ display:none; }}
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# NAVBAR (pure HTML)
# ─────────────────────────────────────────────────────────────────────────────
def render_navbar():
    st.markdown("""
<div class="navbar">
  <div class="navbar-logo">InsightBot</div>
  <nav class="navbar-links">
    <a href="#features" class="navbar-link">Features</a>
    <a href="#process"  class="navbar-link">Process</a>
    <a href="#stack"    class="navbar-link">Stack</a>
  </nav>
  <div class="navbar-right"></div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
def render_hero():
    dm = st.session_state.dark_mode
    random.seed(77)
    dark_colors  = ['rgba(192,132,252,.70)','rgba(168,85,247,.65)',
                    'rgba(99,102,241,.60)','rgba(139,92,246,.70)','rgba(255,255,255,.30)']
    light_colors = ['rgba(124,58,237,.45)','rgba(147,51,234,.40)',
                    'rgba(99,102,241,.45)','rgba(168,85,247,.45)','rgba(167,139,250,.50)']
    colors = dark_colors if dm else light_colors

    dots = ""
    for i in range(30):
        sz  = round(random.uniform(2.5, 6.5), 1)
        lft = round(random.uniform(2, 98), 1)
        bot = round(random.uniform(0, 30), 1)
        dur = round(random.uniform(10, 24), 1)
        dly = round(random.uniform(0, 20), 1)
        col = colors[i % len(colors)]
        gs  = int(sz * 2.2)
        dots += (f'<div class="dot" style="width:{sz}px;height:{sz}px;left:{lft}%;'
                 f'bottom:{bot}px;background:{col};box-shadow:0 0 {gs}px {col};'
                 f'animation-duration:{dur}s;animation-delay:{dly}s;"></div>\n')

    st.markdown(f"""
<div class="hero-wrapper">
  <div class="hero-orb-l"></div>
  <div class="hero-orb-r"></div>
  <div class="hero-glow"></div>
  {dots}
  <div class="hero-content">
    <div class="hero-badge">
      <span class="badge-text">✦ AI-Powered Data Intelligence Platform</span>
    </div>
    <h1 class="hero-title">
      Turn Your Data Into<br/>
      <span class="gradient-text">Actionable Insights</span>
    </h1>
    <p class="hero-desc">
      Upload CSVs, Excel files, or PDFs and instantly get AI-generated
      analysis, beautiful visualizations, and conversational Q&amp;A —
      no coding required.
    </p>
    <a href="/login" target="_self" class="hero-cta">&#9654;&nbsp; Get Started </a>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# STATS
# ─────────────────────────────────────────────────────────────────────────────
def render_stats():
    st.markdown("""
<div class="stats-section">
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
              gap:1rem;max-width:1100px;margin:0 auto;">
    <div class="stat-card"><div class="stat-number">3+</div><div class="stat-label">File Formats</div></div>
    <div class="stat-card"><div class="stat-number">10+</div><div class="stat-label">Chart Types</div></div>
    <div class="stat-card"><div class="stat-number">3</div><div class="stat-label">LLM Providers</div></div>
    <div class="stat-card"><div class="stat-number">100%</div><div class="stat-label">No Code Required</div></div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CAPABILITIES
# ─────────────────────────────────────────────────────────────────────────────
def render_capabilities():
    st.markdown('<div class="section" id="features">', unsafe_allow_html=True)
    st.markdown("""
<div style="text-align:center; display:flex; flex-direction:column; align-items:center;">
  <span class="section-badge">Platform Capabilities</span>
  <h2 class="section-title">Everything You Need</h2>
  <p class="section-sub">A complete data intelligence platform — from raw file to boardroom insight.</p>
</div>""", unsafe_allow_html=True)

    caps = [
        ('01','<svg viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>','Secure Authentication','Full login and signup with bcrypt password hashing. User data is isolated, encrypted, and persistent across sessions.'),
        ('02','<svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>','Multi-Format Upload','Upload CSV, Excel (.xlsx/.xls), and PDF files up to 100 MB. Resume any previous file without re-uploading.'),
        ('03','<svg viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>','Automated EDA','Instant exploratory analysis covering shape, types, missing values, distributions, outliers, and correlations.'),
        ('04','<svg viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>','Dynamic Visualizations','Six chart types via a custom builder: scatter, bar, line, histogram, box, and pie — all rendered interactively with Plotly.'),
        ('05','<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>','AI-Generated Insights','Powered by Groq, OpenAI GPT-4o, or Google Gemini. Executive-level summaries and pattern detection with one click.'),
        ('06','<svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>','Conversational Q&A','Ask questions in plain English. Pandas-powered direct computation with LLM fallback for complex analytical queries.'),
        ('07','<svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>','PDF Document Q&A','FAISS vector indexing over PDF content enables accurate, context-aware retrieval-augmented generation answers.'),
        ('08','<svg viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8"/><path d="M12 17v4"/><path d="M7 9h2l2 4 2-6 2 4h2"/></svg>','AutoML Predictions','Automated machine learning pipeline that trains, evaluates, and explains classification and regression models — no code needed.'),
        ('09','<svg viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>','History & Report Export','Every session persisted. Resume any past conversation and download a full structured analysis report for stakeholders.'),
    ]
    cards_html = '<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:1.5rem; align-items:stretch;">'
    for n, icon, title, desc in caps:
        cards_html += f"""
<div class="card" style="display:flex; flex-direction:column;">
  <div class="card-number">{n}</div>
  <div class="icon-wrap">{icon}</div>
  <h3 class="card-title">{title}</h3>
  <p class="card-desc" style="flex:1;">{desc}</p>
</div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# WORKFLOW
# ─────────────────────────────────────────────────────────────────────────────
def render_workflow():
    st.markdown('<div class="section-alt" id="process">', unsafe_allow_html=True)
    st.markdown("""
<div style="text-align:center; display:flex; flex-direction:column; align-items:center;">
  <span class="section-badge">Workflow</span>
  <h2 class="section-title">From Data to Decision in Four Steps</h2>
  <p class="section-sub">A streamlined process designed to eliminate friction between raw data and actionable intelligence.</p>
</div>""", unsafe_allow_html=True)

    steps = [
        ('01','<svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>','Create Account','Sign up in seconds. Files, analyses, and conversations are securely stored per account.'),
        ('02','<svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>','Upload Your File','Drop any CSV, Excel, or PDF. Automatic format detection and parsing happens instantly.'),
        ('03','<svg viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>','Explore & Predict','Auto-generated charts, AI insights, and AutoML predictive models appear immediately after upload.'),
        ('04','<svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>','Chat & Export','Ask natural language questions and download a structured analysis report for your team.'),
    ]
    wf_html = '<div style="display:grid; grid-template-columns:repeat(4,1fr); gap:1.5rem; align-items:stretch;">'
    for n, icon, title, desc in steps:
        wf_html += f"""
<div class="workflow-card" style="display:flex; flex-direction:column;">
  <div class="workflow-badge">{n}</div>
  <div class="icon-wrap">{icon}</div>
  <h3 class="card-title">{title}</h3>
  <p class="card-desc" style="flex:1;">{desc}</p>
</div>"""
    wf_html += '</div>'
    st.markdown(wf_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TECHNOLOGY
# ─────────────────────────────────────────────────────────────────────────────
def render_technology():
    st.markdown('<div class="section" id="stack">', unsafe_allow_html=True)
    st.markdown("""
<div style="text-align:center; display:flex; flex-direction:column; align-items:center;">
  <span class="section-badge">Technology</span>
  <h2 class="section-title">Built on a Modern, Scalable Foundation</h2>
  <p class="section-sub">Every layer chosen for reliability, speed and intelligence.</p>
</div>""", unsafe_allow_html=True)

    techs = [
        ('Interface',              '<svg viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>',  'Reactive Web Framework',     'A reactive web application framework delivers a fast, responsive UI — every interaction updates in real time.'),
        ('Data Engine',            '<svg viewBox="0 0 24 24"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>', 'Industry-Standard Libraries','Industry-standard tabular data libraries handle everything from simple aggregations to complex transformations.'),
        ('Visualization',          '<svg viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',              'Interactive Charts',         'Interactive, publication-quality charts — zoom, filter, and export any visual with a single click.'),
        ('AI & LLMs',              '<svg viewBox="0 0 24 24"><path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2v-4M9 21H5a2 2 0 0 1-2-2v-4m0 0h18"/></svg>',       'Multi-Provider AI',          'A modular LLM abstraction layer connects to three leading providers — ultra-fast inference and frontier reasoning.'),
        ('Document Intelligence',  '<svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/></svg>', 'Vector Search',     'A vector database indexes document chunks semantically, enabling retrieval-augmented generation in milliseconds.'),
        ('Security',               '<svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',                                                                                'Secure Data Storage',        'A lightweight relational database stores all user data with parameterized queries and standard password hashing.'),
    ]
    cols = st.columns(3)
    tech_html = '<div style="display:grid; grid-template-columns:repeat(3,1fr); gap:1.5rem; align-items:stretch;">'
    for cat, icon, title, desc in techs:
        tech_html += f"""
<div class="card" style="display:flex; flex-direction:column;">
  <div class="icon-wrap">{icon}</div>
  <div class="card-number">{cat}</div>
  <h3 class="card-title">{title}</h3>
  <p class="card-desc" style="flex:1;">{desc}</p>
</div>"""
    tech_html += '</div>'
    st.markdown(tech_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CTA + FOOTER
# ─────────────────────────────────────────────────────────────────────────────
def render_cta():
    st.markdown("""
<div class="cta-section">
  <h2 class="cta-title">Ready to Analyze Your Data?</h2>
  <p class="cta-desc">Get AI-powered insights from your datasets in minutes.</p>
  <a href="/login" target="_self" class="cta-btn-w">&#9654;&nbsp; Get Started </a>
</div>
""", unsafe_allow_html=True)


def render_footer():
    st.markdown("""
<div class="custom-footer">
  <div class="footer-content">
    <div class="footer-logo">InsightBot</div>
    <div class="footer-text">Final Year Project &bull; Avantika &amp; Geeta Bhatt</div>
    <div class="footer-text">AI-Powered Data Intelligence Platform</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN — ORDER MATTERS: toggle first, then everything else
# ─────────────────────────────────────────────────────────────────────────────
def main():
    render_toggle()    # MUST be first — puts button in correct DOM position
    load_css()
    render_navbar()
    render_hero()
    render_stats()
    render_capabilities()
    render_workflow()
    render_technology()
    render_cta()
    render_footer()

if __name__ == "__main__":
    main()