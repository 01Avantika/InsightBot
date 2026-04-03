"""
pages/chat.py — Fixed: proper Q&A, rendered markdown, no duplicates
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from db.database import save_message, get_user_chats, clear_chat
from utils.llm import answer_data_question, pandas_query, answer_pdf_question, get_llm_provider, call_llm
import pandas as pd
import numpy as np

st.set_page_config(page_title="InsightBot — Chat", page_icon="💬", layout="wide")

if not st.session_state.get("user"):
    st.warning("Please login first.")
    st.switch_page("pages/login.py")

user        = st.session_state["user"]
upload      = st.session_state.get("current_upload", {})
df          = st.session_state.get("current_df")
df_summary  = st.session_state.get("current_df_summary", "")
vectorstore = st.session_state.get("current_vectorstore")
pdf_text    = st.session_state.get("current_pdf_text", "")

st.markdown("""
<style>
    [data-testid="stSidebarNav"] { display: none; }

    .context-badge {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(124,58,237,0.3);
        border-radius: 8px; padding: 0.5rem 1rem;
        margin-bottom: 1rem; font-size: 0.9rem;
        color: var(--text-color);
    }
    div.stButton > button {
        background: linear-gradient(135deg, #7c3aed, #a78bfa) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; font-weight: 600 !important;
    }
    /* Style native chat messages */
    div[data-testid="stChatMessage"] {
        border-radius: 12px !important;
        padding: 0.5rem !important;
    }
    .user-profile-footer {
        display: flex; align-items: center; gap: 12px; padding: 12px;
        border-radius: 12px; background-color: var(--secondary-background-color);
        border: 1px solid rgba(124,58,237,0.2); margin-top: 10px;
    }
    .user-avatar {
        width: 40px; height: 40px; background-color: #7c3aed; color: white !important;
        border-radius: 50%; display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 1.1rem; flex-shrink: 0;
    }
    .user-name  { font-weight: 600; font-size: 0.9rem; color: var(--text-color); }
    .user-email { font-size: 0.75rem; color: var(--text-color); opacity: 0.6; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='margin-bottom:2rem; display:flex; align-items:center; gap:10px;'>
            <div style='font-size:26px;'>🤖</div>
            <div style='font-weight:700; font-size:20px; color:#7c3aed;'>InsightBot</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### Navigation")
    st.page_link("pages/dashboard.py", label="Dashboard",       icon="📊")
    st.page_link("pages/analyze.py",   label="Upload & Analyze", icon="📁")
    st.page_link("pages/chat.py",      label="Chat with Data",   icon="💬")
    st.page_link("pages/history.py",   label="History",          icon="📜")

    st.divider()

    if upload:
        ft = upload.get("file_type", "")
        st.markdown(f"**📄 Active File:**\n`{upload.get('filename','')}`")
        if ft in ("csv","xlsx","xls") and df is not None:
            st.info(f"📊 {df.shape[0]:,} rows × {df.shape[1]} cols")
        elif ft == "pdf":
            if vectorstore: st.success("🔍 FAISS Index Ready")
            else:           st.warning("Text mode (no index)")
    else:
        st.info("No file loaded.\nGo to Upload & Analyze first.")

    if st.button("Clear Chat", use_container_width=True):
        uid = upload.get("id") if upload else None
        clear_chat(user["id"], uid)
        st.session_state["chat_history"] = []
        st.rerun()

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    st.divider()

    u_name    = user.get("username", "User")
    u_email   = user.get("email", "")
    u_initial = u_name[0].upper()

    st.markdown(f"""
        <div class="user-profile-footer">
            <div class="user-avatar">{u_initial}</div>
            <div>
                <div class="user-name">{u_name}</div>
                <div class="user-email">{u_email}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Logout", use_container_width=True, key="logout_btn"):
        st.session_state.clear()
        st.switch_page("pages/login.py")

# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("# 💬 Chat with Your Data")

if not upload:
    st.warning("⚠️ No file loaded. Please upload a file first.")
    if st.button("📁 Go to Upload"):
        st.switch_page("pages/analyze.py")
    st.stop()

ft   = upload.get("file_type", "")
icon = "📊" if ft in ("csv","xlsx","xls") else "📄"
mode = "Data Analysis" if ft in ("csv","xlsx","xls") else "Document Q&A"
st.markdown(f"""<div class="context-badge">
    {icon} <b>{upload['filename']}</b> &nbsp;·&nbsp; Mode: <b>{mode}</b>
    {'&nbsp;·&nbsp; 🔍 FAISS Indexed' if vectorstore else ''}
</div>""", unsafe_allow_html=True)

# ── Load persisted chat history ONCE ─────────────────────────────────────────
if "chat_history" not in st.session_state:
    persisted = get_user_chats(user["id"], upload.get("id"))
    st.session_state["chat_history"] = [
        {"role": m["role"], "message": m["message"]} for m in persisted
    ]

# ── Suggestion chips — use pending state to avoid duplicate on rerun ──────────
if ft in ("csv","xlsx","xls"):
    suggestions = [
        "Give me a full statistical summary",
        "Which columns have missing values?",
        "Show correlation between numeric columns",
        "How many unique values in each column?",
    ]
else:
    suggestions = [
        "Summarize this document",
        "What are the main topics?",
        "List key findings",
        "What conclusions are drawn?",
    ]

st.markdown("**💡 Quick Questions:**")
chip_cols = st.columns(4)
for i, sug in enumerate(suggestions):
    if chip_cols[i].button(sug, key=f"chip_{i}"):
        st.session_state["pending_question"] = sug
        st.rerun()

# ── Render existing chat history with native components ───────────────────────
for msg in st.session_state["chat_history"]:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["message"])

# ── Smart Pandas engine ───────────────────────────────────────────────────────
def smart_pandas_answer(question: str, df: pd.DataFrame):
    """
    Returns (answer_str, result_dataframe_or_None).
    Covers 15+ query types with proper formatted markdown output.
    """
    q = question.lower().strip()
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()
    result_df = None
    lines = []

    try:
        # ── Summary / describe ────────────────────────────────────────────────
        if any(w in q for w in ["statistic", "summary", "describe", "overview", "full stat"]):
            result_df = df.describe().round(3)
            lines = [
                f"**Dataset Overview**",
                f"- **Rows:** {df.shape[0]:,} &nbsp;|&nbsp; **Columns:** {df.shape[1]}",
                f"- **Numeric columns:** {len(num_cols)} &nbsp;|&nbsp; **Categorical columns:** {len(cat_cols)}",
                f"- **Total missing values:** {df.isnull().sum().sum():,}",
                f"- **Duplicate rows:** {df.duplicated().sum():,}",
                "",
                "**Descriptive Statistics:**",
            ]

        # ── Missing values ────────────────────────────────────────────────────
        elif any(w in q for w in ["missing", "null", "nan", "empty"]):
            miss = df.isnull().sum()
            miss_pct = (df.isnull().mean() * 100).round(2)
            miss_df = pd.DataFrame({"Missing Count": miss, "Missing %": miss_pct})
            miss_df = miss_df[miss_df["Missing Count"] > 0].sort_values("Missing Count", ascending=False)
            if len(miss_df):
                result_df = miss_df
                lines = [
                    f"**Missing Values** found in **{len(miss_df)}** out of {df.shape[1]} columns:",
                    f"- Total missing cells: **{miss.sum():,}** ({(miss.sum()/(df.shape[0]*df.shape[1])*100):.2f}% of dataset)",
                ]
            else:
                lines = ["✅ **No missing values** found in any column. The dataset is complete."]

        # ── Correlation ───────────────────────────────────────────────────────
        elif any(w in q for w in ["correlation", "corr", "relate", "relationship"]):
            if len(num_cols) >= 2:
                corr = df[num_cols].corr().round(3)
                result_df = corr
                # Find strongest correlations
                pairs = []
                for i in range(len(corr.columns)):
                    for j in range(i+1, len(corr.columns)):
                        pairs.append((corr.columns[i], corr.columns[j], corr.iloc[i,j]))
                pairs.sort(key=lambda x: abs(x[2]), reverse=True)
                top = pairs[:3]
                top_str = "\n".join([f"  - **{a}** ↔ **{b}**: `{v:.3f}`" for a,b,v in top])
                lines = [
                    f"**Correlation Matrix** for {len(num_cols)} numeric columns:",
                    f"",
                    f"**Top correlations:**",
                    top_str,
                ]
            else:
                lines = ["⚠️ Need at least 2 numeric columns to compute correlation."]

        # ── Shape / size ──────────────────────────────────────────────────────
        elif any(w in q for w in ["shape", "size", "dimension", "how many row", "how many col", "rows", "columns"]):
            lines = [
                f"**Dataset Dimensions:**",
                f"- **Rows:** {df.shape[0]:,}",
                f"- **Columns:** {df.shape[1]}",
                f"- **Total cells:** {df.shape[0]*df.shape[1]:,}",
                f"- **Numeric columns:** {len(num_cols)} ({', '.join(num_cols[:5])}{'...' if len(num_cols)>5 else ''})",
                f"- **Categorical columns:** {len(cat_cols)} ({', '.join(cat_cols[:5])}{'...' if len(cat_cols)>5 else ''})",
            ]

        # ── Head / top rows ───────────────────────────────────────────────────
        elif any(w in q for w in ["top 5", "first 5", "head", "top rows", "first rows", "preview", "sample"]):
            result_df = df.head(5)
            lines = [f"**First 5 rows** of `{upload.get('filename','dataset')}`"]

        # ── Unique values ─────────────────────────────────────────────────────
        elif any(w in q for w in ["unique", "distinct", "cardinality"]):
            uniq_df = pd.DataFrame({
                "Column": df.columns,
                "Type": df.dtypes.astype(str),
                "Unique Values": df.nunique(),
                "Unique %": (df.nunique() / len(df) * 100).round(1)
            }).sort_values("Unique Values", ascending=False)
            result_df = uniq_df
            lines = [f"**Unique Value Counts** per column ({df.shape[1]} columns, {df.shape[0]:,} rows):"]

        # ── Duplicates ────────────────────────────────────────────────────────
        elif "duplicate" in q:
            n = df.duplicated().sum()
            pct = n / len(df) * 100
            lines = [
                f"**Duplicate Rows:** {n:,} ({pct:.2f}% of {len(df):,} total rows)",
                f"{'⚠️ Consider removing duplicates before analysis.' if n > 0 else '✅ No duplicates found — dataset is clean.'}",
            ]

        # ── Mean / average ────────────────────────────────────────────────────
        elif any(w in q for w in ["mean", "average", "avg"]):
            if num_cols:
                means = df[num_cols].mean().round(4).reset_index()
                means.columns = ["Column", "Mean"]
                result_df = means
                lines = [f"**Column Means** for {len(num_cols)} numeric columns:"]
            else:
                lines = ["⚠️ No numeric columns found."]

        # ── Max ───────────────────────────────────────────────────────────────
        elif any(w in q for w in ["maximum", "max", "highest", "largest"]):
            if num_cols:
                maxs = df[num_cols].max().reset_index()
                maxs.columns = ["Column", "Maximum"]
                result_df = maxs
                lines = [f"**Maximum Values** for {len(num_cols)} numeric columns:"]

        # ── Min ───────────────────────────────────────────────────────────────
        elif any(w in q for w in ["minimum", "min", "lowest", "smallest"]):
            if num_cols:
                mins = df[num_cols].min().reset_index()
                mins.columns = ["Column", "Minimum"]
                result_df = mins
                lines = [f"**Minimum Values** for {len(num_cols)} numeric columns:"]

        # ── Column info ───────────────────────────────────────────────────────
        elif any(w in q for w in ["column", "feature", "field", "attribute", "list col"]):
            col_df = pd.DataFrame({
                "Column": df.columns,
                "Type": df.dtypes.astype(str),
                "Non-Null": df.notnull().sum(),
                "Null": df.isnull().sum(),
                "Unique": df.nunique()
            })
            result_df = col_df
            lines = [f"**Column Information** — {df.shape[1]} columns total:"]

        # ── Value counts ──────────────────────────────────────────────────────
        elif any(w in q for w in ["count", "frequency", "distribution", "most common", "popular"]):
            target_col = None
            for c in df.columns:
                if c.lower() in q:
                    target_col = c
                    break
            if target_col is None and cat_cols:
                target_col = cat_cols[0]
            if target_col:
                vc = df[target_col].value_counts().head(15).reset_index()
                vc.columns = [target_col, "Count"]
                vc["Percentage"] = (vc["Count"] / len(df) * 100).round(2)
                result_df = vc
                lines = [f"**Value Distribution** for `{target_col}` (top 15 of {df[target_col].nunique()} unique values):"]
            elif num_cols:
                result_df = df[num_cols].describe().round(3)
                lines = ["**Distribution Statistics** for numeric columns:"]

        # ── Sum ───────────────────────────────────────────────────────────────
        elif any(w in q for w in ["sum", "total"]):
            if num_cols:
                sums = df[num_cols].sum().round(4).reset_index()
                sums.columns = ["Column", "Sum"]
                result_df = sums
                lines = [f"**Column Totals** for {len(num_cols)} numeric columns:"]

        # ── Data types ────────────────────────────────────────────────────────
        elif any(w in q for w in ["type", "dtype", "datatype", "data type"]):
            dtype_df = pd.DataFrame({
                "Column": df.columns,
                "Data Type": df.dtypes.astype(str),
                "Non-Null Count": df.notnull().sum(),
                "Sample Value": [str(df[c].dropna().iloc[0]) if len(df[c].dropna()) > 0 else "N/A" for c in df.columns]
            })
            result_df = dtype_df
            lines = [f"**Data Types** for all {df.shape[1]} columns:"]

        # ── Outliers ──────────────────────────────────────────────────────────
        elif any(w in q for w in ["outlier", "anomaly", "unusual", "extreme"]):
            if num_cols:
                outlier_info = []
                for col in num_cols:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)]
                    outlier_info.append({
                        "Column": col,
                        "Outlier Count": len(outliers),
                        "Outlier %": round(len(outliers)/len(df)*100, 2),
                        "Lower Bound": round(Q1 - 1.5*IQR, 3),
                        "Upper Bound": round(Q3 + 1.5*IQR, 3)
                    })
                result_df = pd.DataFrame(outlier_info).sort_values("Outlier Count", ascending=False)
                total_outliers = sum(r["Outlier Count"] for r in outlier_info)
                lines = [
                    f"**Outlier Analysis** using IQR method:",
                    f"- Total outlier cells detected: **{total_outliers:,}**",
                ]

    except Exception as e:
        lines = [f"⚠️ Computation error: {e}"]

    answer = "\n".join(lines) if lines else ""
    return answer, result_df


# ── Handle input ──────────────────────────────────────────────────────────────
pending  = st.session_state.pop("pending_question", None)
question = st.chat_input("Ask anything about your data…")

if pending and not question:
    question = pending

if question:
    # 1. Show user message immediately
    st.session_state["chat_history"].append({"role": "user", "message": question})
    save_message(user["id"], "user", question, upload.get("id"))

    with st.chat_message("user"):
        st.markdown(question)

    # 2. Generate and show assistant response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing…"):
            answer = ""
            result_df = None

            if ft in ("csv","xlsx","xls") and df is not None:

                # Try smart pandas first
                pandas_ans, result_df = smart_pandas_answer(question, df)

                if pandas_ans:
                    st.markdown(pandas_ans)
                    if result_df is not None:
                        st.dataframe(result_df, use_container_width=True)

                    # Add LLM insight on top of computed result
                    provider = get_llm_provider()
                    if provider != "fallback" and df_summary:
                        try:
                            insight = call_llm(
                                f"User asked: '{question}'\n"
                                f"Computed data result shown above.\n"
                                f"Dataset context: {df_summary[:600]}\n\n"
                                f"In 2-3 sentences, give a specific business interpretation of what this result means.",
                                system="You are a concise data analyst. Give specific, actionable insight. No generic statements.",
                                max_tokens=250
                            )
                            if insight and not insight.startswith("["):
                                st.markdown("---")
                                st.markdown(f"**💡 Insight:** {insight}")
                                answer = pandas_ans + "\n\n💡 Insight: " + insight
                            else:
                                answer = pandas_ans
                        except Exception:
                            answer = pandas_ans
                    else:
                        answer = pandas_ans

                else:
                    # Complex / natural language → full LLM
                    system = (
                        "You are an expert data analyst. Answer questions about datasets clearly and specifically.\n"
                        "Always include:\n"
                        "- A direct answer first\n"
                        "- Specific numbers where possible\n"
                        "- Bullet points for lists\n"
                        "- Bold for key findings\n"
                        "Never say 'I cannot analyze' — use the dataset context to give your best answer."
                    )
                    history_ctx = "\n".join([
                        f"{'User' if m['role']=='user' else 'Assistant'}: {m['message'][:200]}"
                        for m in st.session_state["chat_history"][-6:-1]
                    ])
                    prompt = (
                        f"Dataset summary:\n{df_summary}\n\n"
                        f"Recent conversation:\n{history_ctx}\n\n"
                        f"Question: {question}\n\n"
                        f"Answer with specific details from the dataset:"
                    )
                    answer = call_llm(prompt, system=system, max_tokens=1200)
                    st.markdown(answer)

            elif ft == "pdf":
                if vectorstore:
                    answer = answer_pdf_question(question, vectorstore, st.session_state["chat_history"][:-1])
                else:
                    answer = call_llm(
                        f"Document:\n{pdf_text[:4000]}\n\nQuestion: {question}",
                        system="Answer based only on the provided document content.",
                    )
                st.markdown(answer)

            if not answer:
                answer = "⚠️ Could not generate a response. Please check your API key in the `.env` file."
                st.markdown(answer)

    # 3. Save to history and DB — NO st.rerun() needed
    st.session_state["chat_history"].append({"role": "assistant", "message": answer})
    save_message(user["id"], "assistant", answer, upload.get("id"))