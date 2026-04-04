import streamlit as st

# Page configuration
st.set_page_config(
    page_title="InsightBot - AI-Powered Data Intelligence Platform",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for theme
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# ── Pick your badge animation: "shimmer_pulse" | "cosmic_border" | "glow_text"
BADGE_EFFECT = "cosmic_border"

def load_css():
    theme_colors = {
        'bg_primary':        '#111827' if st.session_state.dark_mode else '#ffffff',
        'bg_secondary':      '#1f2937' if st.session_state.dark_mode else '#faf5ff',
        'bg_gradient_start': '#1f2937' if st.session_state.dark_mode else '#faf5ff',
        'bg_gradient_end':   '#111827' if st.session_state.dark_mode else '#ffffff',
        'text_primary':      '#ffffff' if st.session_state.dark_mode else '#111827',
        'text_secondary':    '#d1d5db' if st.session_state.dark_mode else '#4b5563',
        'purple_primary':    '#7c3aed' if st.session_state.dark_mode else '#9333ea',
        'purple_secondary':  '#a78bfa' if st.session_state.dark_mode else '#7c3aed',
        'border_color':      '#374151' if st.session_state.dark_mode else '#e9d5ff',
        'card_bg':           '#1f2937' if st.session_state.dark_mode else '#ffffff',
        'card_hover_bg':     '#374151' if st.session_state.dark_mode else '#faf5ff',
    }

    icon_bg       = 'rgba(167, 139, 250, 0.15)' if st.session_state.dark_mode else 'rgba(147, 51, 234, 0.08)'
    icon_bg_hover = 'rgba(167, 139, 250, 0.28)' if st.session_state.dark_mode else 'rgba(147, 51, 234, 0.18)'
    icon_color    = '#a78bfa'                    if st.session_state.dark_mode else '#7c3aed'
    icon_shadow   = 'rgba(167, 139, 250, 0.35)' if st.session_state.dark_mode else 'rgba(147, 51, 234, 0.22)'

    # ── Badge background / border for each effect ──────────────────────────
    badge_bg     = 'rgba(31, 41, 55, 0.55)'    if st.session_state.dark_mode else 'rgba(255, 255, 255, 0.55)'
    badge_border = '#374151'                    if st.session_state.dark_mode else '#e9d5ff'

    css = f"""
    <style>
        /* ── CSS variables for easy tweaking ─────────────────────────── */
        :root {{
            --ai-purple:      #9333ea;
            --ai-violet:      #7c3aed;
            --ai-indigo:      #6366f1;
            --ai-blue:        #3b82f6;
            --ai-silver:      #e2e8f0;
            --ai-glow-color:  rgba(147, 51, 234, 0.55);
            --badge-bg:       {badge_bg};
            --badge-border:   {badge_border};
        }}

        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
        * {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }}

        .main .block-container {{
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            max-width: 100% !important;
        }}

        .stApp {{
            background: linear-gradient(to bottom,
                {theme_colors['bg_gradient_start']},
                {theme_colors['bg_gradient_end']},
                {theme_colors['bg_gradient_start']});
            transition: all 0.3s ease;
        }}

        /* ============================================================
           GLASSMORPHISM ICON SYSTEM
        ============================================================ */
        .icon-wrap {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 52px; height: 52px;
            border-radius: 14px;
            background: {icon_bg};
            border: 1px solid rgba(147, 51, 234, 0.18);
            box-shadow: 0 4px 16px {icon_shadow}, inset 0 1px 0 rgba(255,255,255,0.12);
            margin-bottom: 1.1rem;
            transition: background 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
            position: relative;
            flex-shrink: 0;
        }}
        .icon-wrap::before {{
            content: '';
            position: absolute; inset: 0;
            border-radius: 14px;
            background: linear-gradient(135deg, rgba(255,255,255,0.10) 0%, transparent 60%);
            pointer-events: none;
        }}
        .icon-wrap svg {{
            width: 22px; height: 22px;
            color: {icon_color}; stroke: {icon_color};
            fill: none; stroke-width: 1.8;
            stroke-linecap: round; stroke-linejoin: round;
            transition: transform 0.25s ease;
            position: relative; z-index: 1;
        }}
        .card:hover .icon-wrap,
        .workflow-card:hover .icon-wrap {{
            background: {icon_bg_hover};
            box-shadow: 0 6px 24px {icon_shadow}, inset 0 1px 0 rgba(255,255,255,0.18);
            transform: translateY(-2px);
        }}
        .card:hover .icon-wrap svg,
        .workflow-card:hover .icon-wrap svg {{ transform: scale(1.10); }}

        /* ============================================================
           GLASSMORPHISM THEME TOGGLE BUTTON
        ============================================================ */
        .stButton > button {{
            background: {icon_bg} !important;
            border: 1px solid rgba(147, 51, 234, 0.18) !important;
            border-radius: 12px !important;
            width: 40px !important; height: 40px !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            font-size: 1.1rem !important;
            line-height: 1 !important;
            box-shadow: 0 4px 16px {icon_shadow}, inset 0 1px 0 rgba(255,255,255,0.12) !important;
            transition: background 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease !important;
            position: relative !important;
            overflow: hidden !important;
        }}
        .stButton > button::before {{
            content: '' !important;
            position: absolute !important; inset: 0 !important;
            border-radius: 12px !important;
            background: linear-gradient(135deg, rgba(255,255,255,0.10) 0%, transparent 60%) !important;
            pointer-events: none !important;
        }}
        .stButton > button:hover {{
            background: {icon_bg_hover} !important;
            border-color: rgba(147, 51, 234, 0.35) !important;
            box-shadow: 0 6px 24px {icon_shadow}, inset 0 1px 0 rgba(255,255,255,0.18) !important;
            transform: translateY(-2px) scale(1.05) !important;
        }}

        /* ============================================================
           AI BADGE — OPTION A: SHIMMERING PULSE (Luxury AI)
           A light streak sweeps L→R every 3 s + breathing purple glow.
        ============================================================ */
        .hero-badge-shimmer {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1.25rem;
            border-radius: 9999px;
            border: 1.5px solid var(--badge-border);
            background: var(--badge-bg);
            backdrop-filter: blur(10px);
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
            /* breathing outer glow */
            animation: badgeGlowBreath 3s ease-in-out infinite;
        }}
        /* the light streak pseudo-element */
        .hero-badge-shimmer::after {{
            content: '';
            position: absolute;
            top: 0; left: -75%;
            width: 50%; height: 100%;
            background: linear-gradient(
                120deg,
                transparent 0%,
                rgba(255,255,255,0.55) 50%,
                transparent 100%
            );
            animation: badgeStreakSweep 3s ease-in-out infinite;
            border-radius: 9999px;
        }}
        @keyframes badgeStreakSweep {{
            0%   {{ left: -75%; opacity: 0; }}
            15%  {{ opacity: 1; }}
            60%  {{ left: 125%; opacity: 1; }}
            61%  {{ opacity: 0; }}
            100% {{ left: 125%; opacity: 0; }}
        }}
        @keyframes badgeGlowBreath {{
            0%,100% {{ box-shadow: 0 0  8px 0px var(--ai-glow-color); }}
            50%      {{ box-shadow: 0 0 20px 4px var(--ai-glow-color); }}
        }}
        .hero-badge-shimmer span {{
            color: var(--ai-violet);
            font-weight: 700; font-size: 0.875rem;
            text-transform: uppercase; letter-spacing: 0.05em;
            position: relative; z-index: 1;
        }}

        /* ============================================================
           AI BADGE — OPTION B: COSMIC BORDER (Neural Network vibe)
           A conic-gradient border rotates continuously.
        ============================================================ */
        .hero-badge-cosmic {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1.25rem;
            border-radius: 9999px;
            margin-bottom: 2rem;
            position: relative;
            /* inner fill */
            background: var(--badge-bg);
            backdrop-filter: blur(10px);
            /* 2-px gap between fill and the spinning border */
            isolation: isolate;
        }}
        /* spinning conic-gradient "border" via ::before */
        .hero-badge-cosmic::before {{
            content: '';
            position: absolute;
            inset: -2px;
            border-radius: 9999px;
            background: conic-gradient(
                from var(--badge-angle, 0deg),
                var(--ai-purple)  0%,
                var(--ai-blue)   25%,
                var(--ai-silver) 50%,
                var(--ai-violet) 75%,
                var(--ai-purple) 100%
            );
            animation: cosmicSpin 3s linear infinite;
            z-index: -1;
        }}
        /* mask the center so only the border ring shows */
        .hero-badge-cosmic::after {{
            content: '';
            position: absolute;
            inset: 1.5px;
            border-radius: 9999px;
            background: var(--badge-bg);
            backdrop-filter: blur(10px);
            z-index: -1;
        }}
        @property --badge-angle {{
            syntax: '<angle>';
            initial-value: 0deg;
            inherits: false;
        }}
        @keyframes cosmicSpin {{
            to {{ --badge-angle: 360deg; }}
        }}
        .hero-badge-cosmic span {{
            color: var(--ai-violet);
            font-weight: 700; font-size: 0.875rem;
            text-transform: uppercase; letter-spacing: 0.05em;
            position: relative; z-index: 1;
        }}

        /* ============================================================
           AI BADGE — OPTION C: GLOWING TEXT SHIMMER
           The text itself animates through purple → blue → silver.
        ============================================================ */
        .hero-badge-glowtext {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1.25rem;
            border-radius: 9999px;
            border: 1.5px solid var(--badge-border);
            background: var(--badge-bg);
            backdrop-filter: blur(10px);
            margin-bottom: 2rem;
        }}
        .hero-badge-glowtext span {{
            font-weight: 700; font-size: 0.875rem;
            text-transform: uppercase; letter-spacing: 0.05em;
            /* moving gradient text */
            background: linear-gradient(
                90deg,
                var(--ai-purple),
                var(--ai-blue),
                var(--ai-silver),
                var(--ai-violet),
                var(--ai-purple)
            );
            background-size: 300% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: glowTextShift 4s linear infinite;
            /* soft drop-shadow glow behind the text */
            filter: drop-shadow(0 0 6px rgba(147, 51, 234, 0.5));
        }}
        @keyframes glowTextShift {{
            0%   {{ background-position: 0%   center; }}
            100% {{ background-position: 300% center; }}
        }}

        /* ============================================================ */

        #MainMenu {{visibility: hidden;}}
        footer    {{visibility: hidden;}}
        header    {{visibility: hidden;}}

        /* ── Navbar ─────────────────────────────────────────────────── */
        .custom-header {{
            position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
            background: {'rgba(17,23,39,0.92)' if st.session_state.dark_mode else 'rgba(255,255,255,0.92)'};
            backdrop-filter: blur(14px);
            border-bottom: 1px solid {theme_colors['border_color']};
            padding: 0 5%;
            display: flex; justify-content: space-between; align-items: center;
            height: 64px;
        }}
        .logo-container {{ flex: 1; }}
        .logo {{
            font-size: 1.5rem; font-weight: 800;
            background: linear-gradient(135deg, #9333ea, #7c3aed);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; width: fit-content;
        }}
        .nav-links {{
            flex: 2; display: flex; justify-content: center;
            gap: 2.5rem; align-items: center;
        }}
        .nav-link {{
            color: {theme_colors['text_primary']} !important;
            text-decoration: none !important;
            font-weight: 700; font-size: 0.9rem;
            text-transform: uppercase; transition: color 0.2s; border: none !important;
        }}
        .nav-link:hover {{ color: #7c3aed !important; text-decoration: none !important; }}

        /* right slot — holds the Streamlit toggle button */
        .nav-right-slot {{
            flex: 1; display: flex; justify-content: flex-end; align-items: center;
        }}

        /* Streamlit column wrapper that carries the button: strip all margins */
        div[data-testid="column"]:last-child {{
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
        }}

        /* ── Hero ───────────────────────────────────────────────────── */
        .hero-section {{
            text-align: center;
            padding: 5rem 2rem 5rem 2rem;
            position: relative; overflow: hidden;
        }}

        .hero-title {{
            font-size: clamp(2.5rem, 5vw, 4.5rem);
            font-weight: 800; margin-bottom: 2rem;
            animation: fadeInUp 0.8s ease-out;
            line-height: 1.2; color: {theme_colors['text_primary']};
        }}

        .gradient-text {{
            background: linear-gradient(135deg, #9333ea, #7c3aed, #6d28d9);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; animation: gradient 3s ease infinite;
            background-size: 200% 200%;
        }}
        @keyframes gradient {{
            0%   {{ background-position: 0%   50%; }}
            50%  {{ background-position: 100% 50%; }}
            100% {{ background-position: 0%   50%; }}
        }}

        .hero-description {{
            font-size: 1.25rem; color: {theme_colors['text_secondary']};
            max-width: 800px;
            margin-left: auto !important; margin-right: auto !important;
            margin-bottom: 3rem; line-height: 1.8;
            text-align: center !important; display: block;
        }}

        .cta-button {{
            display: inline-flex; align-items: center; justify-content: center;
            gap: 0.5rem; padding: 1rem 2rem;
            background: linear-gradient(135deg, #9333ea, #7c3aed);
            color: white !important; border-radius: 0.75rem;
            font-weight: 700; font-size: 1.125rem;
            text-decoration: none !important;
            box-shadow: 0 20px 25px -5px rgba(147,51,234,0.5);
            transition: all 0.3s; animation: fadeInUp 1.2s ease-out;
            border: none; cursor: pointer;
        }}
        .cta-button:hover {{
            transform: scale(1.05);
            box-shadow: 0 25px 30px -5px rgba(147,51,234,0.6);
        }}

        /* ── Stats ───────────────────────────────────────────────────── */
        .stats-section {{
            background: {theme_colors['card_bg']};
            border-top: 1px solid {theme_colors['border_color']};
            border-bottom: 1px solid {theme_colors['border_color']};
            padding: 4rem 2rem; margin: 2rem 0;
        }}
        .stat-card {{ text-align: center; padding: 2rem; transition: transform 0.3s; }}
        .stat-card:hover {{ transform: scale(1.05); }}
        .stat-number {{
            font-size: 3rem; font-weight: 800;
            background: linear-gradient(135deg, #9333ea, #7c3aed);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text; margin-bottom: 0.5rem;
        }}
        .stat-label {{
            font-size: 0.875rem; font-weight: 700;
            color: {theme_colors['text_secondary']};
            text-transform: uppercase; letter-spacing: 0.1em;
        }}

        /* ── Sections ────────────────────────────────────────────────── */
        .section {{ padding: 5rem 2rem; }}
        .section-badge {{
            display: inline-block; padding: 0.5rem 1rem;
            border-radius: 9999px;
            background: {'rgba(124,58,237,0.1)' if st.session_state.dark_mode else 'rgba(147,51,234,0.1)'};
            color: {theme_colors['purple_primary']};
            font-weight: 700; font-size: 0.875rem;
            text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1.5rem;
        }}
        .section-title {{
            font-size: clamp(2rem, 4vw, 3rem); font-weight: 800;
            color: {theme_colors['text_primary']}; margin-bottom: 1rem; text-align: center;
        }}

        /* ── Cards ───────────────────────────────────────────────────── */
        .card {{
            background: {theme_colors['card_bg']};
            border: 1px solid {theme_colors['border_color']};
            border-radius: 1rem; padding: 2rem;
            transition: all 0.3s; height: 100%; position: relative;
        }}
        .card:hover {{
            border-color: {theme_colors['purple_primary']};
            box-shadow: 0 20px 25px -5px rgba(147,51,234,0.1);
            transform: translateY(-5px);
        }}
        .card-number {{
            color: {theme_colors['purple_secondary']};
            font-weight: 700; font-size: 0.875rem;
            letter-spacing: 0.1em; margin-bottom: 1rem;
        }}
        .card-title {{
            font-size: 1.25rem; font-weight: 800;
            color: {theme_colors['text_primary']}; margin-bottom: 1rem;
        }}
        .card-description {{ color: {theme_colors['text_secondary']}; line-height: 1.7; }}

        .workflow-card {{
            background: linear-gradient(135deg, {theme_colors['card_bg']}, {theme_colors['card_hover_bg']});
            border: 1px solid {theme_colors['border_color']};
            border-radius: 1rem; padding: 2rem;
            transition: all 0.3s; height: 100%;
        }}
        .workflow-card:hover {{
            border-color: {theme_colors['purple_primary']};
            box-shadow: 0 20px 25px -5px rgba(147,51,234,0.1);
            transform: translateY(-10px);
        }}
        .workflow-badge {{
            display: flex; align-items: center; justify-content: center;
            width: 4rem; height: 4rem; border-radius: 1rem;
            background: linear-gradient(135deg, #9333ea, #7c3aed);
            color: white; font-weight: 800; font-size: 1.25rem; margin-bottom: 1rem;
            box-shadow: 0 10px 15px -3px rgba(147,51,234,0.5); transition: transform 0.3s;
        }}
        .workflow-card:hover .workflow-badge {{ transform: scale(1.1); }}

        /* ── CTA ─────────────────────────────────────────────────────── */
        .cta-section {{
            background: linear-gradient(135deg, #9333ea, #7c3aed, #6d28d9);
            padding: 6rem 2rem; text-align: center; position: relative; overflow: hidden;
        }}
        .cta-section::before {{
            content: ''; position: absolute; top: 0; left: 25%;
            width: 24rem; height: 24rem;
            background: rgba(147,51,234,0.2); border-radius: 50%;
            filter: blur(80px); animation: pulse 3s ease-in-out infinite;
        }}
        .cta-section::after {{
            content: ''; position: absolute; bottom: 0; right: 25%;
            width: 24rem; height: 24rem;
            background: rgba(124,58,237,0.2); border-radius: 50%;
            filter: blur(80px); animation: pulse 3s ease-in-out infinite; animation-delay: 1s;
        }}
        .cta-title {{
            font-size: clamp(2rem, 4vw, 3.5rem); font-weight: 800;
            color: #ffffff !important; margin-bottom: 1.5rem;
            position: relative; z-index: 10;
        }}
        .cta-description {{
            font-size: 1.25rem; color: rgba(255,255,255,0.9) !important;
            margin-bottom: 2rem; position: relative; z-index: 10;
        }}
        .cta-button-white {{
            display: inline-flex; align-items: center; gap: 0.5rem;
            padding: 1rem 2rem; background: white; color: #7c3aed !important;
            border-radius: 0.75rem; font-weight: 700; font-size: 1.125rem;
            text-decoration: none !important;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
            transition: all 0.3s; border: none; cursor: pointer;
            position: relative; z-index: 10;
        }}
        .cta-button-white:hover {{
            transform: scale(1.05);
            box-shadow: 0 30px 60px -12px rgba(0,0,0,0.35);
        }}

        /* ── Footer ──────────────────────────────────────────────────── */
        .custom-footer {{
            background: {theme_colors['card_bg']};
            border-top: 1px solid {theme_colors['border_color']};
            padding: 2rem; text-align: center;
        }}
        .footer-content {{
            display: flex; justify-content: space-between; align-items: center;
            flex-wrap: wrap; gap: 1rem; max-width: 1200px; margin: 0 auto;
        }}
        .footer-logo {{
            font-size: 1.25rem; font-weight: 800;
            background: linear-gradient(135deg, #9333ea, #7c3aed);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .footer-text {{ color: {theme_colors['text_secondary']}; font-size: 0.875rem; }}

        /* ── Keyframes ───────────────────────────────────────────────── */
        @keyframes fadeInUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to   {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes pulse {{
            0%,100% {{ opacity: 1; }}
            50%      {{ opacity: 0.5; }}
        }}

        @media (max-width: 768px) {{
            .hero-title {{ font-size: 2rem; }}
            .hero-description {{ font-size: 1rem; }}
            .section {{ padding: 3rem 1rem; }}
            .footer-content {{ flex-direction: column; text-align: center; }}
            .nav-links {{ display: none; }}
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Navbar — toggle button sits flush inside the right slot via st.columns
# ---------------------------------------------------------------------------
def render_navbar():
    st.markdown(f"""
    <div class="custom-header">
        <div class="logo-container"><div class="logo">InsightBot</div></div>
        <div class="nav-links">
            <a href="#features" class="nav-link">Features</a>
            <a href="#process"  class="nav-link">Process</a>
            <a href="#stack"    class="nav-link">Stack</a>
        </div>
        <div class="nav-right-slot" id="nav-toggle-anchor"></div>
    </div>
    <style>
        /* Pull the Streamlit column widget into the fixed navbar */
        section[data-testid="stMain"] > div > div[data-testid="stVerticalBlock"]
            > div:first-child
            > div[data-testid="stHorizontalBlock"] {{
            position: fixed;
            top: 12px;
            right: 4%;
            z-index: 1001;
            width: auto !important;
            gap: 0 !important;
            background: transparent !important;
        }}
        /* hide the empty left column */
        section[data-testid="stMain"] > div > div[data-testid="stVerticalBlock"]
            > div:first-child
            > div[data-testid="stHorizontalBlock"]
            > div[data-testid="column"]:first-child {{
            display: none !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    # Two columns: giant spacer + single button cell
    _, btn_col = st.columns([20, 1])
    with btn_col:
        icon = "☀️" if st.session_state.dark_mode else "🌙"
        if st.button(icon, key="theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()


# ---------------------------------------------------------------------------
# Hero  — badge class chosen by BADGE_EFFECT constant at the top
# ---------------------------------------------------------------------------
def render_hero():
    badge_class = {
        "shimmer_pulse":  "hero-badge-shimmer",
        "cosmic_border":  "hero-badge-cosmic",
        "glow_text":      "hero-badge-glowtext",
    }.get(BADGE_EFFECT, "hero-badge-cosmic")

    hero_html = f"""
<div class="hero-section" style="text-align: center;">
    <div class="{badge_class}">
        <span>✨ AI-POWERED DATA INTELLIGENCE PLATFORM</span>
    </div>
    <h1 class="hero-title">
        Turn Your Data Into<br/>
        <span class="gradient-text">Actionable Insights</span>
    </h1>
    <div style="max-width: 800px; margin: 0 auto; text-align: center;">
        <p class="hero-description">
            Upload CSVs, Excel files, or PDFs and instantly get AI-generated
            analysis, beautiful visualizations, and conversational Q&amp;A — no
            coding required.
        </p>
    </div>
    <div style="display: flex; justify-content: center; margin-top: 20px;">
        <a href="/login" target="_self" class="cta-button"
           style="text-decoration:none; display:inline-flex; align-items:center;
                  justify-content:center; white-space:nowrap;">
            GET STARTED
        </a>
    </div>
</div>
"""
    st.markdown(hero_html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------
def render_stats():
    st.markdown("""
    <div class="stats-section">
        <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
                    gap:2rem; max-width:1200px; margin:0 auto;">
            <div class="stat-card"><div class="stat-number">3+</div><div class="stat-label">FILE FORMATS</div></div>
            <div class="stat-card"><div class="stat-number">10+</div><div class="stat-label">CHART TYPES</div></div>
            <div class="stat-card"><div class="stat-number">3</div><div class="stat-label">LLM PROVIDERS</div></div>
            <div class="stat-card"><div class="stat-number">100%</div><div class="stat-label">NO CODE REQUIRED</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Capabilities
# ---------------------------------------------------------------------------
def render_capabilities():
    st.markdown('<div class="section" id="features">', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;"><span class="section-badge">Platform Capabilities</span></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Everything You Need</h2>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; color:#4b5563; margin-bottom:3rem;">A complete data intelligence platform — from raw file to boardroom insight.</div>', unsafe_allow_html=True)

    capabilities = [
        {'number':'01','icon':'<svg viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>','title':'Secure Authentication','description':'Full login and signup with bcrypt password hashing. User data is isolated, encrypted, and persistent across sessions.'},
        {'number':'02','icon':'<svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>','title':'Multi-Format Upload','description':'Upload CSV, Excel (.xlsx/.xls), and PDF files up to 100 MB. Resume any previous file without re-uploading.'},
        {'number':'03','icon':'<svg viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>','title':'Automated EDA','description':'Instant exploratory analysis covering shape, types, missing values, distributions, outliers, and correlations — generated automatically.'},
        {'number':'04','icon':'<svg viewBox="0 0 24 24"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>','title':'Dynamic Visualizations','description':'Six chart types via a custom builder: scatter, bar, line, histogram, box, and pie — all rendered interactively with Plotly.'},
        {'number':'05','icon':'<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>','title':'AI-Generated Insights','description':'Powered by Groq, OpenAI GPT-4o, or Google Gemini. Executive-level summaries and pattern detection with one click.'},
        {'number':'06','icon':'<svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>','title':'Conversational Q&A','description':'Ask questions in plain English. Pandas-powered direct computation with LLM fallback for complex analytical queries.'},
        {'number':'07','icon':'<svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>','title':'PDF Document Q&A','description':'FAISS vector indexing over PDF content enables accurate, context-aware retrieval-augmented generation answers.'},
        {'number':'08','icon':'<svg viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8"/><path d="M12 17v4"/><path d="M7 9h2l2 4 2-6 2 4h2"/></svg>','title':'AutoML Predictions','description':'Automated machine learning pipeline that trains, evaluates, and explains classification and regression models on your dataset — no code needed.'},
        {'number':'09','icon':'<svg viewBox="0 0 24 24"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>','title':'History & Report Export','description':'Every session persisted. Resume any past conversation and download a full structured analysis report for stakeholders.'},
    ]

    cols = st.columns(3)
    for idx, cap in enumerate(capabilities):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="card">
                <div class="card-number">{cap['number']}</div>
                <div class="icon-wrap">{cap['icon']}</div>
                <h3 class="card-title">{cap['title']}</h3>
                <p class="card-description">{cap['description']}</p>
            </div><br/>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Workflow
# ---------------------------------------------------------------------------
def render_workflow():
    st.markdown('<div class="section" id="process">', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;"><span class="section-badge">Workflow</span></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">From Data to Decision in Four Steps</h2>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; color:#4b5563; max-width:700px; margin:0 auto 3rem auto;">A streamlined process designed to eliminate friction between raw data and actionable intelligence.</div>', unsafe_allow_html=True)

    steps = [
        {'number':'01','icon':'<svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>','title':'Create Account','description':'Sign up in seconds. Files, analyses, and conversations are securely stored per account.'},
        {'number':'02','icon':'<svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>','title':'Upload Your File','description':'Drop any CSV, Excel, or PDF. Automatic format detection and parsing happens instantly.'},
        {'number':'03','icon':'<svg viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>','title':'Explore & Predict','description':'Auto-generated charts, AI insights, and AutoML predictive models appear immediately after upload.'},
        {'number':'04','icon':'<svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>','title':'Chat & Export','description':'Ask natural language questions and download a structured analysis report for your team.'},
    ]

    cols = st.columns(4)
    for idx, step in enumerate(steps):
        with cols[idx]:
            st.markdown(f"""
            <div class="workflow-card">
                <div class="workflow-badge">{step['number']}</div>
                <div class="icon-wrap" style="margin-bottom:0.8rem;">{step['icon']}</div>
                <h3 class="card-title">{step['title']}</h3>
                <p class="card-description">{step['description']}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Technology
# ---------------------------------------------------------------------------
def render_technology():
    st.markdown('<div class="section" id="stack">', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center;"><span class="section-badge">Technology</span></div>', unsafe_allow_html=True)
    st.markdown('<h2 class="section-title">Built on a Modern, Scalable Foundation</h2>', unsafe_allow_html=True)
    st.markdown('<div style="text-align:center; color:#4b5563; max-width:700px; margin:0 auto 3rem auto;">Every layer chosen for reliability, speed and intelligence.</div>', unsafe_allow_html=True)

    technologies = [
        {'category':'INTERFACE','icon':'<svg viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>','title':'Reactive Web Framework','description':'A reactive web application framework delivers a fast, responsive UI with zero HTML — every interaction updates in real time without page reloads.'},
        {'category':'DATA ENGINE','icon':'<svg viewBox="0 0 24 24"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>','title':'Industry-Standard Libraries','description':'Industry-standard tabular data libraries handle everything from simple aggregations to complex transformations on datasets of any size.'},
        {'category':'VISUALIZATION','icon':'<svg viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>','title':'Interactive Charts','description':'Interactive, publication-quality charts powered by a modern charting library — zoom, filter, and export any visual with a single click.'},
        {'category':'AI & LANGUAGE MODELS','icon':'<svg viewBox="0 0 24 24"><path d="M9 3H5a2 2 0 0 0-2 2v4m6-6h10a2 2 0 0 1 2 2v4M9 3v18m0 0h10a2 2 0 0 0 2-2v-4M9 21H5a2 2 0 0 1-2-2v-4m0 0h18"/></svg>','title':'Multi-Provider AI','description':'A modular LLM abstraction layer connects to three leading providers — ultra-fast inference, frontier reasoning, and cost-efficient options are all supported interchangeably.'},
        {'category':'DOCUMENT INTELLIGENCE','icon':'<svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>','title':'Vector Search','description':'A vector database indexes document chunks semantically, enabling retrieval-augmented generation that finds the right answer from thousands of pages in milliseconds.'},
        {'category':'PERSISTENCE & SECURITY','icon':'<svg viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>','title':'Secure Data Storage','description':'A lightweight relational database stores all user data with parameterized queries and industry-standard password hashing — zero plaintext credentials.'},
    ]

    cols = st.columns(3)
    for idx, tech in enumerate(technologies):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="card">
                <div class="icon-wrap">{tech['icon']}</div>
                <div class="card-number">{tech['category']}</div>
                <h3 class="card-title">{tech['title']}</h3>
                <p class="card-description">{tech['description']}</p>
            </div><br/>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# CTA + Footer
# ---------------------------------------------------------------------------
def render_cta():
    st.markdown("""
    <div class="cta-section">
        <h2 class="cta-title">Ready to Analyze Your Data?</h2>
        <p class="cta-description">Get AI-powered insights from your datasets in minutes.</p>
        <a href="/login" target="_self" class="cta-button-white">GET STARTED</a>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    st.markdown("""
    <div class="custom-footer">
        <div class="footer-content">
            <div class="footer-logo">InsightBot</div>
            <div class="footer-text">Final Year Project • Avantika &amp; Geeta Bhatt</div>
            <div class="footer-text">AI-Powered Data Intelligence Platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
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