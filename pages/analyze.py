"""
pages/analyze.py — Fixed duplicate keys + delete file feature
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from db.database import save_upload, save_analysis, get_user_uploads, init_db
from utils.file_handler import save_uploaded_file, get_file_extension, extract_pdf_text, format_file_size, get_pdf_page_count
from utils.eda import load_file, get_basic_stats, get_summary_text, auto_generate_charts
from utils.llm import generate_insights, get_llm_provider

init_db()

st.set_page_config(page_title="InsightBot — Upload & Analyze", page_icon="📁", layout="wide")

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
    .stat-box { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 1rem; text-align: center; }
    .stat-val  { font-size: 1.8rem; font-weight: 700; color: #a78bfa; }
    .stat-lbl  { color: #94a3b8; font-size: 0.8rem; }
    div.stButton > button {
        background: linear-gradient(135deg, #7c3aed, #a78bfa) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
    }
    [data-testid="stSidebar"] { background: #1e293b !important; }
    .file-card {
        background: rgba(124,58,237,0.08); border: 1px solid rgba(167,139,250,0.25);
        border-radius: 12px; padding: 0.8rem 1rem; margin-bottom: 0.5rem;
    }
    .tag { display: inline-block; padding: 0.15rem 0.55rem; border-radius: 20px; font-size: 0.72rem; font-weight: 700; }
    .tag-csv  { background: #065f46; color: #6ee7b7; }
    .tag-pdf  { background: #7f1d1d; color: #fca5a5; }
    .tag-xlsx { background: #1e3a5f; color: #93c5fd; }
</style>
            
            provider = get_llm_provider()
    if provider == "groq":     st.success("🟢 Groq Connected")
    elif provider == "openai": st.success("🟢 OpenAI Connected")
    elif provider == "gemini": st.success("🟢 Gemini Connected")
    else:                      st.warning("🟡 No LLM API Key\nAdd key to .env")
    st.divider()
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"### 👤 {user['username']}")
    st.divider()
    st.page_link("pages/dashboard.py", label="📊 Dashboard")
    st.page_link("pages/chat.py",      label="💬 Chat with Data")
    st.page_link("pages/history.py",   label="📜 History")
    st.divider()
    if st.button("Logout"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.switch_page("pages/login.py")

st.markdown("# 📁 Upload & Analyze")
st.markdown("<p style='color:#94a3b8'>Upload a new file or resume working on a previous one</p>", unsafe_allow_html=True)

tab_new, tab_resume = st.tabs(["📤 Upload New File", "📂 Resume Previous File"])


def render_analysis(file_path, ext, filename, upload_id, prefix=""):
    """prefix makes all widget keys unique between tabs."""
    k = f"{prefix}_{upload_id}"

    if ext in ("csv", "xlsx", "xls"):
        if st.session_state.get("loaded_upload_id") != upload_id:
            df = load_file(file_path, ext)
            st.session_state["current_df"]         = df
            st.session_state["current_df_summary"] = get_summary_text(df)
            st.session_state["loaded_upload_id"]   = upload_id

        df    = st.session_state["current_df"]
        stats = get_basic_stats(df)
        rows, cols_n = stats["shape"]

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f'<div class="stat-box"><div class="stat-val">{rows:,}</div><div class="stat-lbl">Rows</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="stat-box"><div class="stat-val">{cols_n}</div><div class="stat-lbl">Columns</div></div>', unsafe_allow_html=True)
        with c3:
            miss = sum(stats["missing"].values())
            st.markdown(f'<div class="stat-box"><div class="stat-val">{miss}</div><div class="stat-lbl">Missing Values</div></div>', unsafe_allow_html=True)
        with c4: st.markdown(f'<div class="stat-box"><div class="stat-val">{stats["duplicates"]}</div><div class="stat-lbl">Duplicates</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">👁️ Data Preview</div>', unsafe_allow_html=True)
        st.dataframe(df.head(50), use_container_width=True, height=280)

        with st.expander("📋 Column Details"):
            col_info = pd.DataFrame({
                "Column": df.columns, "Type": df.dtypes.astype(str),
                "Non-Null": df.notnull().sum(), "Null %": (df.isnull().mean()*100).round(1),
                "Unique": df.nunique(),
            })
            st.dataframe(col_info, use_container_width=True)

        with st.expander("📈 Descriptive Statistics"):
            num_df = df.select_dtypes(include="number")
            if not num_df.empty:
                st.dataframe(num_df.describe().round(3), use_container_width=True)
            else:
                st.info("No numeric columns found.")

        st.markdown('<div class="section-header">📊 Auto-Generated Visualizations</div>', unsafe_allow_html=True)
        charts = auto_generate_charts(df)
        for i in range(0, len(charts), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(charts):
                    title, fig = charts[i + j]
                    with col:
                        st.plotly_chart(fig, use_container_width=True, key=f"auto_chart_{k}_{i}_{j}")

        st.markdown('<div class="section-header">🎨 Custom Chart Builder</div>', unsafe_allow_html=True)
        num_cols = df.select_dtypes(include="number").columns.tolist()
        all_cols = df.columns.tolist()
        cc1, cc2, cc3, cc4 = st.columns(4)
        with cc1: chart_type = st.selectbox("Chart Type", ["Scatter","Bar","Line","Histogram","Box","Pie"], key=f"ct_{k}")
        with cc2: x_col      = st.selectbox("X Axis", all_cols, key=f"xc_{k}")
        with cc3: y_col      = st.selectbox("Y Axis", num_cols if num_cols else all_cols, key=f"yc_{k}")
        with cc4: color_col  = st.selectbox("Color By", ["None"] + all_cols, key=f"cc_{k}")

        if st.button("🎨 Generate Chart", key=f"chart_btn_{k}"):
            import plotly.express as px
            color = None if color_col == "None" else color_col
            try:
                if chart_type == "Scatter":     fig = px.scatter(df, x=x_col, y=y_col, color=color, opacity=0.6)
                elif chart_type == "Bar":       fig = px.bar(df, x=x_col, y=y_col, color=color)
                elif chart_type == "Line":      fig = px.line(df, x=x_col, y=y_col, color=color)
                elif chart_type == "Histogram": fig = px.histogram(df, x=x_col, color=color)
                elif chart_type == "Box":       fig = px.box(df, x=color, y=y_col)
                elif chart_type == "Pie":
                    vc = df[x_col].value_counts().head(10)
                    fig = px.pie(values=vc.values, names=vc.index, title=f"{x_col} Distribution")
                fig.update_layout(template="plotly_dark", height=420)
                st.plotly_chart(fig, use_container_width=True, key=f"custom_chart_{k}")
            except Exception as e:
                st.error(f"Chart error: {e}")

        st.markdown('<div class="section-header">🧠 AI-Generated Insights</div>', unsafe_allow_html=True)
        if st.button("✨ Generate AI Insights", type="primary", key=f"insights_btn_{k}"):
            with st.spinner("🤖 Analyzing your dataset…"):
                summary  = get_summary_text(df)
                insights = generate_insights(summary, filename)
                save_analysis(user["id"], upload_id, summary, insights)
                st.session_state["last_insights"] = insights

        if st.session_state.get("last_insights"):
            st.markdown(st.session_state["last_insights"])
            if st.button("💬 Chat About This Data", key=f"goto_chat_{k}"):
                st.switch_page("pages/chat.py")

    elif ext == "pdf":
        if st.session_state.get("loaded_upload_id") != upload_id:
            with st.spinner("Extracting PDF content…"):
                pdf_text = extract_pdf_text(file_path)
                st.session_state["current_pdf_text"] = pdf_text
                st.session_state["current_pdf_path"] = file_path
                st.session_state["loaded_upload_id"] = upload_id

        pages = get_pdf_page_count(file_path)
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div class="stat-box"><div class="stat-val">{pages}</div><div class="stat-lbl">Pages</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="stat-box"><div class="stat-val">{format_file_size(os.path.getsize(file_path))}</div><div class="stat-lbl">File Size</div></div>', unsafe_allow_html=True)

        with st.expander("📄 View Extracted Text", expanded=False):
            st.text(st.session_state.get("current_pdf_text","")[:3000])

        st.markdown('<div class="section-header">🔍 Build Document Index for Q&A</div>', unsafe_allow_html=True)
        if st.button("🔍 Index Document", key=f"index_btn_{k}"):
            with st.spinner("Building FAISS vector index…"):
                from utils.llm import build_faiss_index
                vectorstore, result = build_faiss_index(file_path)
                if vectorstore:
                    st.session_state["current_vectorstore"] = vectorstore
                    st.success(f"✅ Indexed! {result} chunks ready for Q&A.")
                    save_analysis(user["id"], upload_id, f"PDF indexed: {result} chunks", "Document indexed for Q&A")
                else:
                    st.warning(f"FAISS index failed: {result}. Text-mode Q&A still available.")

        st.markdown('<div class="section-header">🧠 AI Document Summary</div>', unsafe_allow_html=True)
        if st.button("✨ Summarize Document", key=f"summarize_btn_{k}"):
            with st.spinner("Summarizing…"):
                from utils.llm import call_llm
                summary = call_llm(
                    f"Summarize this document:\n\n{st.session_state.get('current_pdf_text','')[:4000]}",
                    system="You are an expert document analyst. Provide a clear, structured summary.",
                )
                save_analysis(user["id"], upload_id, "PDF text preview", summary)
                st.markdown(summary)


# ── Tab 1: Upload New File ────────────────────────────────────────────────────
with tab_new:
    uploaded = st.file_uploader(
        "Drop your file here or click to browse",
        type=["csv", "xlsx", "xls", "pdf"],
        key="file_uploader"
    )

    if uploaded:
        file_key = f"{uploaded.name}_{uploaded.size}"
        if st.session_state.get("last_uploaded_key") != file_key:
            file_bytes = uploaded.read()
            ext        = get_file_extension(uploaded.name)
            file_path, file_size = save_uploaded_file(file_bytes, uploaded.name, user["id"])
            upload_id  = save_upload(user["id"], uploaded.name, ext, file_path, file_size)
            st.session_state["current_upload"]    = {"id": upload_id, "filename": uploaded.name, "file_type": ext, "file_path": file_path}
            st.session_state["last_uploaded_key"] = file_key
            st.session_state["loaded_upload_id"]  = None
            st.session_state["last_insights"]     = None
            st.session_state["chat_history"]      = []
            st.success(f"✅ **{uploaded.name}** uploaded! ({format_file_size(uploaded.size)})")

        upload = st.session_state.get("current_upload", {})
        if upload:
            st.markdown(f'<div class="section-header">📊 Analysis — {upload["filename"]}</div>', unsafe_allow_html=True)
            render_analysis(upload["file_path"], upload["file_type"], upload["filename"], upload["id"], prefix="new")


# ── Tab 2: Resume / Delete Previous File ─────────────────────────────────────
with tab_resume:
    st.markdown('<div class="section-header">📂 Your Previous Files</div>', unsafe_allow_html=True)
    prev_uploads = get_user_uploads(user["id"])

    if not prev_uploads:
        st.info("No previous files found. Upload a file first.")
    else:
        st.markdown("<p style='color:#94a3b8'>Load to resume analysis · Delete to remove permanently</p>", unsafe_allow_html=True)

        for u in prev_uploads:
            ext = u["file_type"]
            tag_cls = f"tag-{ext}" if ext in ("csv","pdf","xlsx") else "tag-csv"
            col1, col2, col3 = st.columns([5, 1, 1])

            with col1:
                st.markdown(f"""<div class="file-card">
                    <span class="tag {tag_cls}">{ext.upper()}</span>
                    &nbsp;<b style='color:#e2e8f0'>{u['filename']}</b>
                    <span style='color:#64748b; font-size:0.8rem; float:right'>{u['uploaded_at'][:16]} · {format_file_size(u.get('file_size',0))}</span>
                </div>""", unsafe_allow_html=True)

            with col2:
                if st.button("▶ Load", key=f"load_{u['id']}"):
                    if os.path.exists(u["file_path"]):
                        st.session_state["current_upload"]   = {"id": u["id"], "filename": u["filename"], "file_type": u["file_type"], "file_path": u["file_path"]}
                        st.session_state["loaded_upload_id"] = None
                        st.session_state["last_insights"]    = None
                        st.session_state["chat_history"]     = []
                        st.success(f"✅ Loaded **{u['filename']}**")
                        st.rerun()
                    else:
                        st.error("File missing on disk. Please re-upload.")

            with col3:
                if st.button("🗑️", key=f"del_{u['id']}", help="Delete this file"):
                    # Delete from disk
                    try:
                        if os.path.exists(u["file_path"]):
                            os.remove(u["file_path"])
                    except Exception:
                        pass
                    # Delete from database
                    import sqlite3
                    from db.database import get_connection
                    conn = get_connection()
                    conn.execute("DELETE FROM uploads WHERE id = ?", (u["id"],))
                    conn.execute("DELETE FROM analyses WHERE upload_id = ?", (u["id"],))
                    conn.execute("DELETE FROM chats WHERE upload_id = ?", (u["id"],))
                    conn.commit()
                    conn.close()
                    # Clear session if it was the active file
                    if st.session_state.get("current_upload", {}).get("id") == u["id"]:
                        st.session_state.pop("current_upload", None)
                        st.session_state.pop("current_df", None)
                        st.session_state.pop("loaded_upload_id", None)
                    st.success(f"🗑️ Deleted **{u['filename']}**")
                    st.rerun()

        # Show analysis for resumed file (only in this tab)
        upload = st.session_state.get("current_upload", {})
        if upload and os.path.exists(upload.get("file_path", "")):
            if any(u["id"] == upload["id"] for u in prev_uploads):
                st.markdown(f'<div class="section-header">📊 Resuming — {upload["filename"]}</div>', unsafe_allow_html=True)
                render_analysis(upload["file_path"], upload["file_type"], upload["filename"], upload["id"], prefix="resume")