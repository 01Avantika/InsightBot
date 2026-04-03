"""
pages/analyze.py — Fixed duplicate keys + delete file feature + Adaptive Theme
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

# ---------------- ADAPTIVE CUSTOM CSS (Light/Dark Mode Fix) ----------------
st.markdown("""
<style>
    /* HIDE DEFAULT STREAMLIT NAV */
    [data-testid="stSidebarNav"] {display: none;}

    /* SECTION HEADERS - Adaptive */
    .section-header {
        font-size: 1.2rem; font-weight: 700; color: var(--text-color);
        border-left: 4px solid #7c3aed; padding-left: 0.75rem; margin: 1.5rem 0 1rem;
    }

    /* STAT BOXES & FILE CARDS - Adaptive Background */
    .stat-box, .file-card { 
        background-color: var(--secondary-background-color); 
        border: 1px solid rgba(124, 58, 237, 0.2); 
        border-radius: 12px; padding: 1rem; text-align: center; 
        margin-bottom: 0.5rem;
    }
    .stat-val { font-size: 1.8rem; font-weight: 700; color: #7c3aed; }
    .stat-lbl { color: var(--text-color); opacity: 0.7; font-size: 0.8rem; }

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
        border: 1px solid rgba(124, 58, 237, 0.2); margin-top: 10px;
    }
    .user-avatar {
        width: 40px; height: 40px; background-color: #7c3aed; color: white !important;
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 1.1rem; flex-shrink: 0;
    }
    .user-name { font-weight: 600; font-size: 0.9rem; color: var(--text-color); }
    .user-email { font-size: 0.75rem; color: var(--text-color); opacity: 0.6; }

    /* FILE TAGS */
    .tag { display: inline-block; padding: 0.15rem 0.55rem; border-radius: 20px; font-size: 0.72rem; font-weight: 700; color: white; }
    .tag-csv  { background: #059669; }
    .tag-pdf  { background: #dc2626; }
    .tag-xlsx { background: #2563eb; }
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
    st.page_link("pages/dashboard.py", label="Dashboard")
    st.page_link("pages/analyze.py",   label="Upload & Analyze")
    st.page_link("pages/automl.py",    label="AutoML")
    st.page_link("pages/chat.py",      label="Chat with Data")
    st.page_link("pages/history.py",   label="History")
    
    
    st.markdown("<div style='flex-grow: 1; height: 100px;'></div>", unsafe_allow_html=True)
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
                
                # Dynamic theme application for Plotly
                fig.update_layout(height=420)
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
                    &nbsp;<b style='color:var(--text-color)'>{u['filename']}</b>
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