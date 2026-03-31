"""
pages/dashboard.py — Main Dashboard
"""

from datetime import datetime

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from db.database import get_user_uploads, get_user_analyses, get_user_chats, init_db
from utils.file_handler import format_file_size

init_db()

st.set_page_config(page_title="InsightBot — Dashboard", page_icon="📊", layout="wide")

if not st.session_state.get("user"):
    st.warning("Please login first.")
    st.switch_page("pages/login.py")

user = st.session_state["user"]

st.markdown("""
<style>
    .stApp { background: #0f172a; color: #e2e8f0; }
    .metric-card {
        background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(167,139,250,0.08));
        border: 1px solid rgba(167,139,250,0.25);
        border-radius: 16px; padding: 1.5rem; text-align: center;
    }
    .metric-num   { font-size: 2.5rem; font-weight: 700; color: #a78bfa; }
    .metric-label { color: #94a3b8; font-size: 0.9rem; margin-top: 0.2rem; }
    .section-header {
        font-size: 1.3rem; font-weight: 700; color: #e2e8f0;
        border-left: 4px solid #7c3aed; padding-left: 0.75rem; margin: 1.5rem 0 1rem;
    }
    .history-row {
        background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px; padding: 1rem; margin-bottom: 0.5rem;
    }
    .tag { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
    .tag-csv  { background: #065f46; color: #6ee7b7; }
    .tag-pdf  { background: #7f1d1d; color: #fca5a5; }
    .tag-xlsx { background: #1e3a5f; color: #93c5fd; }
    div.stButton > button {
        background: linear-gradient(135deg, #7c3aed, #a78bfa) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
    }
    [data-testid="stSidebar"] { background: #1e293b !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"### 👤 {user['username']}")
    st.markdown(f"<small style='color:#94a3b8'>{user['email']}</small>", unsafe_allow_html=True)
    st.divider()
    st.page_link("pages/analyze.py",  label="📁 Upload & Analyze")
    st.page_link("pages/chat.py",     label="💬 Chat with Data")
    st.page_link("pages/history.py",  label="📜 History")
    st.divider()
    if st.button(" Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.switch_page("pages/login.py")

st.markdown(f"# 🤖 InsightBot Dashboard")
st.markdown(f"<p style='color:#94a3b8'>Good day, <b style='color:#a78bfa'>{user['username']}</b>! Here's your analytics overview.</p>", unsafe_allow_html=True)

uploads   = get_user_uploads(user["id"])
analyses  = get_user_analyses(user["id"])
chats     = get_user_chats(user["id"])
user_msgs = [c for c in chats if c["role"] == "user"]

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

st.markdown('<div class="section-header"> Quick Actions</div>', unsafe_allow_html=True)
qa1, qa2, qa3, qa4 = st.columns(4)
with qa1:
    if st.button(" Upload New File", use_container_width=True):
        st.switch_page("pages/analyze.py")
with qa2:
    if st.button(" Start Chatting", use_container_width=True):
        st.switch_page("pages/chat.py")
with qa3:
    if st.button(" View History", use_container_width=True):
        st.switch_page("pages/history.py")

with qa4:
    if st.button(" Download Report", use_container_width=True):
        st.session_state["show_report"] = not st.session_state.get("show_report", False)
        st.rerun()

# ── Report Download
if st.session_state.get("show_report"):
    st.markdown('<div class="section-header"> Download Report</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown(f'<div class="account-card">', unsafe_allow_html=True)
 
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        report_lines = [
            "=" * 60,
            "           INSIGHTBOT — ANALYSIS REPORT",
            "=" * 60,
            f"Generated : {now}",
            f"User      : {user['username']} ({user['email']})",
            "",
            "─" * 60,
            "SUMMARY",
            "─" * 60,
            f"Total Files Uploaded : {len(uploads)}",
            f"Total Analyses Run   : {len(analyses)}",
            f"Total Questions Asked: {len(user_msgs)}",
            f"Total Data Processed : {total_mb:.2f} MB",
            "",
        ]
 
        if uploads:
            report_lines += ["─" * 60, "FILES UPLOADED", "─" * 60]
            for u in uploads:
                report_lines.append(f"  • [{u['file_type'].upper()}] {u['filename']} — {format_file_size(u.get('file_size',0))} — {u['uploaded_at'][:16]}")
            report_lines.append("")
 
        if analyses:
            report_lines += ["─" * 60, "AI INSIGHTS & ANALYSES", "─" * 60]
            for a in analyses:
                report_lines.append(f"\n File: {a['filename']}  |  Date: {a['created_at'][:16]}")
                report_lines.append("-" * 40)
                if a.get("insights"):
                    # Strip markdown for plain text
                    insight_text = a["insights"].replace("**", "").replace("*", "").replace("#", "")
                    report_lines.append(insight_text)
                report_lines.append("")
 
        if user_msgs:
            report_lines += ["─" * 60, "CONVERSATION HISTORY", "─" * 60]
            for c in chats[-50:]:
                role = "You" if c["role"] == "user" else "InsightBot"
                report_lines.append(f"[{c['created_at'][11:16]}] {role}: {c['message'][:200]}")
            report_lines.append("")
 
        report_lines += ["=" * 60, "End of Report — InsightBot AI Analytics Platform", "=" * 60]
        report_text = "\n".join(report_lines)
 
        col_prev, col_dl = st.columns([3, 1])
        with col_prev:
            st.text_area("Report Preview", report_text[:800] + "\n\n... (full report in download)", height=200, disabled=True)
        with col_dl:
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label=" Download .txt",
                data=report_text,
                file_name=f"insightbot_report_{user['username']}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
            # CSV summary download
            if uploads:
                import pandas as pd
                df_report = pd.DataFrame([{
                    "Filename": u["filename"],
                    "Type": u["file_type"],
                    "Size": format_file_size(u.get("file_size",0)),
                    "Uploaded": u["uploaded_at"][:16],
                } for u in uploads])
                csv_data = df_report.to_csv(index=False)
                st.download_button(
                    label=" Download CSV",
                    data=csv_data,
                    file_name=f"insightbot_uploads_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
 
        if st.button("✕ Close Report", key="close_report"):
            st.session_state["show_report"] = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section-header">📁 Recent Uploads</div>', unsafe_allow_html=True)
if not uploads:
    st.info("No files uploaded yet. Start by uploading a CSV, Excel, or PDF file!")
else:
    for u in uploads[:5]:
        ext = u["file_type"]
        tag_cls = f"tag-{ext}" if ext in ("csv","pdf","xlsx") else "tag-csv"
        st.markdown(f"""<div class="history-row">
            <span class="tag {tag_cls}">{ext.upper()}</span>
            &nbsp;&nbsp;<b>{u['filename']}</b>
            <span style="color:#64748b;font-size:0.8rem;float:right">{u['uploaded_at'][:16]} &nbsp;|&nbsp; {format_file_size(u.get('file_size',0))}</span>
        </div>""", unsafe_allow_html=True)

st.markdown('<div class="section-header">📊 Recent Analyses</div>', unsafe_allow_html=True)
if not analyses:
    st.info("No analyses yet. Upload a dataset and run EDA to see results here.")
else:
    for a in analyses[:3]:
        with st.expander(f"🔍 {a['filename']} — {a['created_at'][:16]}"):
            st.markdown(a["insights"] or a["analysis"][:500] + "…")
