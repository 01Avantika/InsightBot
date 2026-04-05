"""
utils/ui_components.py — Shared Sidebar + UI Utilities
Provides render_sidebar() that matches the Dashboard sidebar exactly,
with resizable drag-handle support for all pages.
"""
import streamlit as st
import streamlit.components.v1 as components


SIDEBAR_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg-base:      #0B0C10;
    --bg-surface:   #12141a;
    --bg-card:      #161922;
    --bg-elevated:  #1c2030;
    --bg-hover:     #1f2638;
    --border:       #23263a;
    --border-l:     #2e3247;
    --text-h:       #f1f5f9;
    --text-b:       #94a3b8;
    --text-dim:     #4b5675;
    --purple:       #b794f4;
    --purple-mid:   #9b72e8;
    --purple-dark:  #7c3aed;
    --purple-dim:   rgba(183,148,244,0.10);
    --purple-glow:  rgba(183,148,244,0.22);
    --r-sm: 8px; --r-md: 12px;
}

*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp {
    font-family: 'Inter', sans-serif !important;
    background: var(--bg-base) !important;
    color: var(--text-h) !important;
}

#MainMenu, footer, header        { visibility: hidden !important; }
[data-testid="stSidebarNav"]     { display: none !important; }
[data-testid="stDecoration"]     { display: none !important; }
.main .block-container           { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stMain"] > div { padding: 0 !important; }

::-webkit-scrollbar              { width: 4px; height: 4px; }
::-webkit-scrollbar-track        { background: var(--bg-base); }
::-webkit-scrollbar-thumb        { background: var(--border-l); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover  { background: var(--purple-dark); }

[data-testid="stSidebar"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: var(--bg-surface) !important;
    border-right: 1px solid var(--border) !important;
    padding: 0 !important;
    transition: background .35s ease;
    transform: none !important;
    position: relative !important;
    overflow: visible !important;
}
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebar"] .block-container { padding: 0 !important; }
[data-testid="collapsedControl"],
button[kind="header"][aria-label*="sidebar"],
[data-testid="stSidebarCollapseButton"] { display: none !important; }

[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {
    display: flex !important; align-items: center !important; gap: 9px !important;
    padding: .5rem 1rem !important; border-radius: var(--r-sm) !important;
    margin: 2px 10px !important; font-size: .82rem !important; font-weight: 500 !important;
    color: var(--text-b) !important; text-decoration: none !important;
    transition: background .18s, color .18s, transform .15s !important;
    position: relative !important;
}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {
    background: var(--purple-dim) !important; color: var(--purple) !important;
    transform: translateX(3px) !important;
}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] {
    background: var(--purple-dim) !important; color: var(--purple) !important; font-weight: 600 !important;
}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"]::before {
    content:''; position:absolute; left:0; top:22%; bottom:22%;
    width:3px; border-radius:0 3px 3px 0; background:var(--purple);
    box-shadow:0 0 8px var(--purple-glow);
}
[data-testid="stSidebar"] h3 {
    font-size:.6rem !important; font-weight:700 !important; letter-spacing:.12em !important;
    text-transform:uppercase !important; color:var(--text-dim) !important;
    padding:1.2rem 1rem .4rem !important; margin:0 !important;
}
[data-testid="stSidebar"] hr { border-color:var(--border) !important; margin:.5rem .75rem !important; }

div.stButton > button {
    background: linear-gradient(135deg,#7c3aed 0%,#5b8dee 100%) !important;
    color:#fff !important; border:none !important; border-radius:var(--r-sm) !important;
    font-weight:600 !important; font-size:.78rem !important; letter-spacing:.02em !important;
    padding:.5rem 1rem !important;
    box-shadow:0 4px 14px rgba(124,58,237,.28) !important;
    transition: opacity .2s, transform .15s, box-shadow .2s !important;
}
div.stButton > button:hover {
    opacity:.88 !important; transform:translateY(-2px) !important;
    box-shadow:0 8px 22px rgba(124,58,237,.45) !important;
}

.sb-logo {
    display:flex; align-items:center; gap:10px;
    padding:1.25rem 1rem 1rem; border-bottom:1px solid var(--border); margin-bottom:.4rem;
}
.sb-logo-icon {
    width:32px; height:32px; border-radius:var(--r-sm);
    background:linear-gradient(135deg,var(--purple-dark),var(--purple));
    display:flex; align-items:center; justify-content:center;
    font-size:18px; flex-shrink:0;
}
.sb-logo-name { font-size:.95rem; font-weight:800; color:var(--text-h); }
.sb-logo-sub  { font-size:.55rem; color:var(--text-dim); letter-spacing:.12em; text-transform:uppercase; }

.sb-user {
    display:flex; align-items:center; gap:9px;
    padding:.65rem 1rem; margin:0 .5rem .5rem;
    border-radius:var(--r-sm); background:var(--bg-elevated);
    border:1px solid var(--border);
}
.sb-avatar {
    width:30px; height:30px; border-radius:50%; flex-shrink:0;
    background:linear-gradient(135deg,var(--purple-dark),var(--purple));
    display:flex; align-items:center; justify-content:center;
    font-size:.78rem; font-weight:700; color:#fff;
}
.sb-uname { font-size:.78rem; font-weight:600; color:var(--text-h); }
.sb-email { font-size:.65rem; color:var(--text-dim);
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:140px; }

.main, section[data-testid="stMain"] { padding-left: 1.5rem !important; }
</style>
"""

_RESIZE_JS = """
<!DOCTYPE html><html><head>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:transparent; overflow:hidden; }
#handle {
  position:fixed; left:226px; top:0; bottom:0; width:8px;
  cursor:col-resize; z-index:999999; background:transparent; transition:background .2s;
}
#handle:hover { background:rgba(183,148,244,.35); }
#handle.dragging { background:rgba(183,148,244,.55); }
</style>
</head><body>
<div id="handle" title="Drag to resize sidebar"></div>
<script>
(function(){
  const KEY='insightbot_sb_width', MIN=180, MAX=420, DEF=230;
  function saved(){ try{return parseInt(localStorage.getItem(KEY))||DEF;}catch(e){return DEF;} }
  function save(w){ try{localStorage.setItem(KEY,w);}catch(e){} }
  function apply(w){
    w=Math.min(MAX,Math.max(MIN,w));
    const sb=window.parent.document.querySelector('[data-testid="stSidebar"]');
    if(!sb) return;
    sb.style.setProperty('min-width',w+'px','important');
    sb.style.setProperty('max-width',w+'px','important');
    sb.style.setProperty('width',w+'px','important');
    document.getElementById('handle').style.left=(w-4)+'px';
  }
  apply(saved());
  const h=document.getElementById('handle');
  let drag=false,sx=0,sw=0;
  h.addEventListener('mousedown',function(e){
    e.preventDefault(); drag=true; sx=e.clientX;
    const sb=window.parent.document.querySelector('[data-testid="stSidebar"]');
    sw=sb?sb.getBoundingClientRect().width:saved();
    h.classList.add('dragging');
    window.parent.document.body.style.userSelect='none';
    window.parent.document.body.style.cursor='col-resize';
  });
  window.addEventListener('mousemove',function(e){
    if(!drag)return; apply(sw+(e.clientX-sx));
  });
  window.addEventListener('mouseup',function(e){
    if(!drag)return; drag=false;
    h.classList.remove('dragging');
    window.parent.document.body.style.userSelect='';
    window.parent.document.body.style.cursor='';
    const sb=window.parent.document.querySelector('[data-testid="stSidebar"]');
    if(sb) save(Math.round(sb.getBoundingClientRect().width));
  });
})();
</script></body></html>
"""


def render_sidebar(user: dict) -> None:
    """
    Renders the shared InsightBot sidebar that matches the Dashboard design exactly.
    Includes a drag-to-resize handle (persisted in localStorage).

    Parameters
    ----------
    user : dict  — session user object (keys: username, email)
    """
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    u_name    = user.get("username", "User")
    u_email   = user.get("email", "user@example.com")
    u_initial = u_name[0].upper() if u_name else "U"

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
        st.page_link("pages/dashboard.py", label="⊞ Dashboard")
        st.page_link("pages/analyze.py",   label="☁ Upload & Analyze")
        st.page_link("pages/automl.py",    label="⚙ AutoML")
        st.page_link("pages/chat.py",      label="🗨 Chat with Data")
        st.page_link("pages/history.py",   label="↺ History")

        for _ in range(9):
            st.markdown("")
        st.markdown("<hr style='border-color:var(--border); margin:.5rem .5rem'/>",
                    unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sb-user">
            <div class="sb-avatar">{u_initial}</div>
            <div style="min-width:0">
                <div class="sb-uname">{u_name}</div>
                <div class="sb-email">{u_email}</div>
            </div>
        </div>""", unsafe_allow_html=True)

        if st.button("Logout", use_container_width=True, key="shared_sidebar_logout"):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.switch_page("pages/login.py")

        # Resize handle (zero-height iframe, purely for JS)
        components.html(_RESIZE_JS, height=0, scrolling=False)
