"""
pages/dashboard.py — Main Dashboard
"""

from datetime import datetime
import streamlit as st
import sys, os

# Ensure project root is in path for database and utility imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from db.database import get_user_uploads, get_user_analyses, get_user_chats, init_db
from utils.file_handler import format_file_size

# Initialize Database
init_db()

# Page Configuration
st.set_page_config(
    page_title="InsightBot — Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- AUTH CHECK ----------------
if not st.session_state.get("user"):
    st.warning("Please login first.")
    st.switch_page("pages/login.py")

user = st.session_state["user"]


# ---------------- CUSTOM CSS (Hides Default Sidebar & Styles UI) ----------------
st.markdown("""
<style>
    /* HIDE DEFAULT STREAMLIT SIDEBAR NAV */
    [data-testid="stSidebarNav"] {display: none;}
    
    /* Global Background Overrides (Removed to allow 3-dot theme switching) */
    
    /* Metric Cards - Glassmorphism style */
    .metric-card {
        background: linear-gradient(135deg, rgba(124,58,237,0.1), rgba(167,139,250,0.05));
        border: 1px solid rgba(167,139,250,0.2);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: transform 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-5px); }
    .metric-num { font-size: 2.5rem; font-weight: 700; color: #a78bfa; }
    .metric-label { font-size: 0.9rem; opacity: 0.7; margin-top: 0.2rem; }

    /* Section Headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        border-left: 4px solid #7c3aed;
        padding-left: 0.75rem;
        margin: 2rem 0 1rem;
    }

    /* History Rows */
    .history-row {
        background: rgba(124,58,237,0.05);
        border: 1px solid rgba(124,58,237,0.1);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.5rem;
    }

    /* File Tags */
    .tag { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
    .tag-csv  { background: #065f46; color: #6ee7b7; }
    .tag-pdf  { background: #7f1d1d; color: #fca5a5; }
    .tag-xlsx { background: #1e3a5f; color: #93c5fd; }

    /* Custom Button Style */
    div.stButton > button {
        background: linear-gradient(135deg, #7c3aed, #a78bfa) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar Profile styling */
    .sidebar-user {
        padding: 10px;
        border-radius: 10px;
        background: rgba(124,58,237,0.1);
        margin-bottom: 20px;
    }
    /* Sidebar User Profile Footer Styling */
    .user-profile-footer {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        border-radius: 12px;
        background: rgba(124, 58, 237, 0.1);
        border: 1px solid rgba(124, 58, 237, 0.2);
        margin-top: 10px;
    }

    .user-avatar {
        width: 40px;
        height: 40px;
        background-color: #7c3aed;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 1.1rem;
        flex-shrink: 0;
    }

    .user-info {
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    .user-name {
        font-weight: 600;
        font-size: 0.9rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .user-email {
        font-size: 0.75rem;
        opacity: 0.7;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- CUSTOM SIDEBAR CONTENT ----------------
# ---------------- CUSTOM SIDEBAR CONTENT ----------------
with st.sidebar:
    # 1. Logo Section
    st.markdown("""
        <div style='margin-bottom:2.5rem; display:flex; align-items:center; gap:10px;'>
            <div style='font-size:28px;'>🤖</div>
            <div style='font-weight:700; font-size:22px; color:#7c3aed;'>InsightBot</div>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. Navigation Links
    st.markdown("### Navigation")
    st.page_link("pages/dashboard.py", label="Dashboard", icon="📊")
    st.page_link("pages/analyze.py",   label="Upload & Analyze", icon="📁")
    st.page_link("pages/chat.py",      label="Chat with Data", icon="💬")
    st.page_link("pages/history.py",   label="History", icon="📜")

    
    
    # 3. Push to bottom
    st.markdown("<div style='flex-grow: 1; height: 100px;'></div>", unsafe_allow_html=True)
    st.divider()

    # 4. User Profile Footer with Circle Avatar
    u_name = user.get('username', 'User')
    u_email = user.get('email', 'user@example.com')
    u_initial = u_name[0].upper() if u_name else "U"

    st.markdown(f"""
        <div class="user-profile-footer">
            <div class="user-avatar">{u_initial}</div>
            <div class="user-info">
                <div class="user-name">{u_name}</div>
                <div class="user-email">{u_email}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.write("") # Spacer

    # 5. Logout Button
    if st.button("Logout", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.switch_page("pages/login.py")

# ---------------- DASHBOARD MAIN CONTENT ----------------
st.markdown("# 🤖 InsightBot Dashboard")
st.markdown(f"<p style='opacity:0.8'>Welcome back, <b style='color:#a78bfa'>{user['username']}</b>! Here is your workspace summary.</p>", unsafe_allow_html=True)

# Fetch Data
uploads   = get_user_uploads(user["id"])
analyses  = get_user_analyses(user["id"])
chats     = get_user_chats(user["id"])
user_msgs = [c for c in chats if c["role"] == "user"]

# 1. Metrics Grid
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-num">{len(uploads)}</div><div class="metric-label">📁 Files Uploaded</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-num">{len(analyses)}</div><div class="metric-label">📊 Analyses Run</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-num">{len(user_msgs)}</div><div class="metric-label">💬 Questions Asked</div></div>', unsafe_allow_html=True)
with col4:
    total_mb = sum(u.get("file_size", 0) for u in uploads) / (1024 * 1024)
    st.markdown(f'<div class="metric-card"><div class="metric-num">{total_mb:.1f}</div><div class="metric-label">💾 MB Processed</div></div>', unsafe_allow_html=True)

# 2. Quick Actions
st.markdown('<div class="section-header">Quick Actions</div>', unsafe_allow_html=True)
qa1, qa2, qa3, qa4 = st.columns(4)
with qa1:
    if st.button("📁 Upload New File", use_container_width=True):
        st.switch_page("pages/analyze.py")
with qa2:
    if st.button("💬 Start Chatting", use_container_width=True):
        st.switch_page("pages/chat.py")
with qa3:
    if st.button("📜 View History", use_container_width=True):
        st.switch_page("pages/history.py")
with qa4:
    if st.button("📥 Download Report", use_container_width=True):
        st.session_state["show_report"] = not st.session_state.get("show_report", False)
        st.rerun()

# 3. Report Section (Conditional)
if st.session_state.get("show_report"):
    st.markdown('<div class="section-header">Download Analytics Report</div>', unsafe_allow_html=True)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    report_text = f"INSIGHTBOT REPORT\nGenerated: {now}\nUser: {user['username']}\nTotal Uploads: {len(uploads)}"
    st.download_button("Click to Download .txt", report_text, file_name=f"report_{user['username']}.txt")

# 4. Recent Activity
left_col, right_col = st.columns([1, 1])

with left_col:
    st.markdown('<div class="section-header">📁 Recent Uploads</div>', unsafe_allow_html=True)
    if not uploads:
        st.info("No files found.")
    else:
        for u in uploads[:5]:
            ext = u["file_type"]
            tag_cls = f"tag-{ext}" if ext in ("csv","pdf","xlsx") else "tag-csv"
            st.markdown(f"""
            <div class="history-row">
                <span class="tag {tag_cls}">{ext.upper()}</span>
                &nbsp;&nbsp;<b>{u['filename']}</b>
                <span style="opacity:0.6; font-size:0.8rem; float:right">{u['uploaded_at'][:10]}</span>
            </div>
            """, unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="section-header">📊 Recent Analyses</div>', unsafe_allow_html=True)
    if not analyses:
        st.info("No analyses run yet.")
    else:
        for a in analyses[:3]:
            with st.expander(f"🔍 {a['filename']}"):
                st.write(a["insights"] or "Detailed analysis available in history.")
