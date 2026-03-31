"""
pages/history.py — Full history with readable conversations + continue chat
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

st.markdown("""
<style>
    .stApp { background: #0f172a; color: #e2e8f0; }
    .section-header {
        font-size: 1.2rem; font-weight: 700; color: #e2e8f0;
        border-left: 4px solid #7c3aed; padding-left: 0.75rem; margin: 1.5rem 0 1rem;
    }
    .history-row {
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.6rem;
    }
    .tag { display: inline-block; padding: 0.2rem 0.65rem; border-radius: 20px; font-size: 0.72rem; font-weight: 700; }
    .tag-csv  { background: #065f46; color: #6ee7b7; }
    .tag-pdf  { background: #7f1d1d; color: #fca5a5; }
    .tag-xlsx { background: #1e3a5f; color: #93c5fd; }
    .chat-bubble-user {
        background: linear-gradient(135deg, #7c3aed, #6d28d9);
        color: white; border-radius: 18px 18px 4px 18px;
        padding: 0.7rem 1rem; margin: 0.4rem 0 0.4rem auto;
        max-width: 75%; width: fit-content; margin-left: auto;
    }
    .chat-bubble-ai {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(167,139,250,0.2);
        color: #e2e8f0; border-radius: 18px 18px 18px 4px;
        padding: 0.7rem 1rem; margin: 0.4rem 0;
        max-width: 80%; width: fit-content;
    }
    .chat-meta { font-size: 0.7rem; color: #475569; margin: 0.1rem 0.3rem; }
    .conv-header {
        background: rgba(124,58,237,0.12); border: 1px solid rgba(167,139,250,0.25);
        border-radius: 10px; padding: 0.6rem 1rem; margin-bottom: 0.8rem;
        display: flex; justify-content: space-between; align-items: center;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #7c3aed, #a78bfa) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
    }
    [data-testid="stSidebar"] { background: #1e293b !important; }
    .empty-state { text-align:center; padding:3rem; color:#64748b; border:1px dashed rgba(255,255,255,0.1); border-radius:16px; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"### 👤 {user['username']}")
    st.divider()
    st.page_link("pages/dashboard.py", label="📊 Dashboard")
    st.page_link("pages/analyze.py",   label="📁 Upload & Analyze")
    st.page_link("pages/chat.py",      label="💬 Chat with Data")
    st.divider()

    if st.button("Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.switch_page("pages/login.py")

st.markdown("# 📜 Activity History")
st.markdown("<p style='color:#94a3b8'>Complete log of your uploads, analyses, and conversations</p>", unsafe_allow_html=True)

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
                <span style="color:#64748b;font-size:0.8rem;float:right">
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

    # Get all uploads to group conversations by file
    all_uploads = get_user_uploads(user["id"])

    if not all_uploads:
        st.markdown('<div class="empty-state">📭 No conversations yet.</div>', unsafe_allow_html=True)
    else:
        # Also fetch conversations with no upload_id
        all_chats = get_user_chats(user["id"])
        if not all_chats:
            st.markdown('<div class="empty-state">📭 No conversations yet. Start chatting with your data!</div>', unsafe_allow_html=True)
        else:
            # Group chats by upload_id
            from collections import defaultdict
            grouped = defaultdict(list)
            for c in all_chats:
                grouped[c.get("upload_id")].append(c)

            # Show conversations per file
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

                    # Continue conversation button
                    col_info, col_btn = st.columns([4, 1])
                    with col_info:
                        st.markdown(f"""
                        <span class="tag {tag_cls}">{ext.upper()}</span>
                        &nbsp;<b style='color:#a78bfa'>{upload['filename']}</b>
                        <span style='color:#64748b; font-size:0.8rem'> · {msg_count} messages · Last: {convos[-1]['created_at'][:16]}</span>
                        """, unsafe_allow_html=True)
                    with col_btn:
                        if st.button("▶ Continue", key=f"continue_{uid}"):
                            # Load this file back into session
                            if os.path.exists(upload["file_path"]):
                                st.session_state["current_upload"] = {
                                    "id": upload["id"],
                                    "filename": upload["filename"],
                                    "file_type": upload["file_type"],
                                    "file_path": upload["file_path"],
                                }
                                # Restore full chat history for this file
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

                    # Render full conversation as chat bubbles
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

            # Show any chats with no upload linked
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
                                <div class="chat-meta"> InsightBot · {timestamp}</div>
                            </div>""", unsafe_allow_html=True)