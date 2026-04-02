"""
pages/history.py — Full history with readable conversations + continue chat + Adaptive Theme
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from db.database import get_user_uploads, get_user_analyses, get_user_chats, init_db, get_connection
from utils.file_handler import format_file_size

init_db()

st.set_page_config(page_title="InsightBot — History", page_icon="📜", layout="wide")

if not st.session_state.get("user"):
    st.warning("Please login first.")
    st.switch_page("pages/login.py")

user = st.session_state["user"]

# ---------------- ADAPTIVE CUSTOM CSS (Light/Dark Mode Fix) ----------------
st.markdown("""
<style>
    /* HIDE DEFAULT STREAMLIT NAV */
    [data-testid="stSidebarNav"] {display: none;}

    .section-header {
        font-size: 1.2rem; font-weight: 700; color: var(--text-color);
        border-left: 4px solid #7c3aed; padding-left: 0.75rem; margin: 1.5rem 0 1rem;
    }
    .history-row {
        background: var(--secondary-background-color); 
        border: 1px solid rgba(124, 58, 237, 0.2);
        border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.6rem;
        color: var(--text-color);
    }
    .tag { display: inline-block; padding: 0.2rem 0.65rem; border-radius: 20px; font-size: 0.72rem; font-weight: 700; }
    .tag-csv  { background: #065f46; color: #6ee7b7; }
    .tag-pdf  { background: #7f1d1d; color: #fca5a5; }
    .tag-xlsx { background: #1e3a5f; color: #93c5fd; }
    
    /* CHAT BUBBLES - Adaptive */
    .chat-bubble-user {
        background: linear-gradient(135deg, #7c3aed, #6d28d9);
        color: white !important; border-radius: 18px 18px 4px 18px;
        padding: 0.7rem 1rem; margin: 0.4rem 0 0.4rem auto;
        max-width: 75%; width: fit-content; margin-left: auto;
    }
    .chat-bubble-ai {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(124, 58, 237, 0.2);
        color: var(--text-color); border-radius: 18px 18px 18px 4px;
        padding: 0.7rem 1rem; margin: 0.4rem 0;
        max-width: 80%; width: fit-content;
    }
    .chat-meta { font-size: 0.7rem; color: var(--text-color); opacity: 0.6; margin: 0.1rem 0.3rem; }
    
    /* BUTTONS */
    div.stButton > button {
        background: linear-gradient(135deg, #7c3aed, #a78bfa) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
        font-weight: 600 !important;
    }

    /* SIDEBAR USER FOOTER */
    .user-profile-footer {
        display: flex; align-items: center; gap: 12px; padding: 12px;
        border-radius: 12px; background-color: var(--secondary-background-color);
        border: 1px solid rgba(124, 58, 237, 0.2); margin-top: 5px;
    }
    .user-avatar {
        width: 40px; height: 40px; background-color: #7c3aed; color: white !important;
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 1.1rem; flex-shrink: 0;
    }
    .user-name { font-weight: 600; font-size: 0.9rem; color: var(--text-color); }
    .user-email { font-size: 0.75rem; color: var(--text-color); opacity: 0.6; }
    
    .empty-state { text-align:center; padding:3rem; color:var(--text-color); opacity:0.5; border:1px dashed rgba(124,58,237,0.3); border-radius:16px; }
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR WITH USER FOOTER ----------------
with st.sidebar:
    st.markdown("""
        <div style='margin-bottom:2.5rem; display:flex; align-items:center; gap:10px;'>
            <div style='font-size:28px;'>🤖</div>
            <div style='font-weight:700; font-size:22px; color:#7c3aed;'>InsightBot</div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Navigation")
    st.page_link("pages/dashboard.py", label="Dashboard", icon="📊")
    st.page_link("pages/analyze.py",   label="Upload & Analyze", icon="📁")
    st.page_link("pages/chat.py",      label="Chat with Data", icon="💬")
    st.page_link("pages/history.py",   label="History", icon="📜")
    
    # Adjusted spacer height to move logout a little further down
    st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
    st.divider()

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

    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/login.py")

# ---------------- MAIN CONTENT ----------------
st.markdown("# 📜 Activity History")
st.markdown("<p style='color:var(--text-color); opacity:0.7'>Complete log of your uploads, analyses, and conversations</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📁 Uploads", "📊 Analyses", "💬 Conversations"])

# ── Uploads ───────────────────────────────────────────────────────────────────
with tab1:
    uploads = get_user_uploads(user["id"])
    st.markdown(f'<div class="section-header">📁 Upload History ({len(uploads)} files)</div>', unsafe_allow_html=True)
    if not uploads:
        st.markdown('<div class="empty-state">📭 No files uploaded yet.</div>', unsafe_allow_html=True)
    else:
        search   = st.text_input("🔍 Search files", placeholder="Filter by filename…")
        filtered = [u for u in uploads if search.lower() in u["filename"].lower()] if search else uploads
        for u in filtered:
            ext = u["file_type"]
            tag_cls = f"tag-{ext}" if ext in ("csv","pdf","xlsx") else "tag-csv"
            st.markdown(f"""<div class="history-row">
                <span class="tag {tag_cls}">{ext.upper()}</span>
                &nbsp;<b>{u['filename']}</b>
                <span style="color:var(--text-color); opacity:0.6; font-size:0.8rem; float:right">
                    {format_file_size(u.get('file_size',0))} &nbsp;|&nbsp; {u['uploaded_at'][:16]}
                </span>
            </div>""", unsafe_allow_html=True)

# ── Analyses ──────────────────────────────────────────────────────────────────
with tab2:
    analyses = get_user_analyses(user["id"])
    st.markdown(f'<div class="section-header">📊 Analysis History ({len(analyses)} analyses)</div>', unsafe_allow_html=True)
    if not analyses:
        st.markdown('<div class="empty-state">📭 No analyses yet.</div>', unsafe_allow_html=True)
    else:
        for a in analyses:
            with st.expander(f"🔍 {a['filename']} — {a['created_at'][:16]}"):
                if a.get("insights"):
                    st.markdown("**AI Insights:**")
                    st.markdown(a["insights"])
                    st.divider()
                st.markdown("**Data Summary:**")
                st.text(a["analysis"][:800] + ("…" if len(a["analysis"]) > 800 else ""))

# ── Conversations ─────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-header">💬 Conversations</div>', unsafe_allow_html=True)

    all_uploads = get_user_uploads(user["id"])

    if not all_uploads:
        st.markdown('<div class="empty-state">📭 No conversations yet.</div>', unsafe_allow_html=True)
    else:
        all_chats = get_user_chats(user["id"])
        if not all_chats:
            st.markdown('<div class="empty-state">📭 No conversations yet. Start chatting with your data!</div>', unsafe_allow_html=True)
        else:
            from collections import defaultdict
            grouped = defaultdict(list)
            for c in all_chats:
                grouped[c.get("upload_id")].append(c)

            for upload in all_uploads:
                uid = upload["id"]
                convos = grouped.get(uid, [])
                if not convos:
                    continue

                ext = upload["file_type"]
                tag_cls = f"tag-{ext}" if ext in ("csv","pdf","xlsx") else "tag-csv"
                msg_count = len(convos)
                user_msgs = len([c for c in convos if c["role"] == "user"])

                with st.expander(f"📄 {upload['filename']}  ·  {user_msgs} questions  ·  {upload['uploaded_at'][:10]}"):
                    col_info, col_btn = st.columns([4, 1])
                    with col_info:
                        st.markdown(f"""
                        <span class="tag {tag_cls}">{ext.upper()}</span>
                        &nbsp;<b style='color:#a78bfa'>{upload['filename']}</b>
                        <span style='color:var(--text-color); opacity:0.6; font-size:0.8rem'> · {msg_count} messages · Last: {convos[-1]['created_at'][:16]}</span>
                        """, unsafe_allow_html=True)
                    with col_btn:
                        if st.button("▶ Continue", key=f"continue_{uid}"):
                            if os.path.exists(upload["file_path"]):
                                st.session_state["current_upload"] = {
                                    "id": upload["id"],
                                    "filename": upload["filename"],
                                    "file_type": upload["file_type"],
                                    "file_path": upload["file_path"],
                                }
                                st.session_state["chat_history"] = [
                                    {"role": c["role"], "message": c["message"]}
                                    for c in convos
                                ]
                                st.session_state["loaded_upload_id"] = None
                                st.success(f"✅ Loaded conversation for **{upload['filename']}** — redirecting to Chat…")
                                st.switch_page("pages/chat.py")
                            else:
                                st.error("Original file not found on disk. Please re-upload it in Upload & Analyze.")

                    st.divider()

                    for msg in convos:
                        timestamp = msg["created_at"][11:16] if len(msg["created_at"]) > 10 else ""
                        if msg["role"] == "user":
                            st.markdown(f"""
                            <div style='text-align:right'>
                                <div class="chat-bubble-user">
                                    {msg['message']}
                                </div>
                                <div class="chat-meta">👤 You · {timestamp}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div>
                                <div class="chat-bubble-ai">
                                    {msg['message']}
                                </div>
                                <div class="chat-meta">🤖 InsightBot · {timestamp}</div>
                            </div>
                            """, unsafe_allow_html=True)

            no_upload_chats = grouped.get(None, [])
            if no_upload_chats:
                with st.expander(f"💬 General Conversations · {len(no_upload_chats)} messages"):
                    for msg in no_upload_chats:
                        timestamp = msg["created_at"][11:16] if len(msg["created_at"]) > 10 else ""
                        if msg["role"] == "user":
                            st.markdown(f"""
                            <div style='text-align:right'>
                                <div class="chat-bubble-user">{msg['message']}</div>
                                <div class="chat-meta">👤 You · {timestamp}</div>
                            </div>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div>
                                <div class="chat-bubble-ai">{msg['message']}</div>
                                <div class="chat-meta">🤖 InsightBot · {timestamp}</div>
                            </div>""", unsafe_allow_html=True)