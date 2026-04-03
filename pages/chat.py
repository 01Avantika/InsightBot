"""
pages/chat.py — Fixed: proper Q&A, rendered markdown, no duplicates, auto-scroll
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
    .user-name  { font-weight: 600; font-size: 0.9rem; }
    .user-email { font-size: 0.75rem; opacity: 0.6; }
    /* anchor target for scroll */
    #chat-bottom { height: 1px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='margin-bottom:2rem;display:flex;align-items:center;gap:10px;'>
            <div style='font-size:26px;'>🤖</div>
            <div style='font-weight:700;font-size:20px;color:#7c3aed;'>InsightBot</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### Navigation")
    st.page_link("pages/dashboard.py", label="Dashboard")
    st.page_link("pages/analyze.py",   label="Upload & Analyze")
    st.page_link("pages/automl.py",    label="AutoML")
    st.page_link("pages/chat.py",      label="Chat with Data")
    st.page_link("pages/history.py",   label="History")

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

# ── Suggestion chips ──────────────────────────────────────────────────────────
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

# ── Render existing chat history ──────────────────────────────────────────────
for msg in st.session_state["chat_history"]:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["message"])

# ── Auto-scroll anchor — always at the bottom of messages ────────────────────
st.markdown('<div id="chat-bottom"></div>', unsafe_allow_html=True)
# JS scroll: runs on every render, scrolls to bottom of page
st.components.v1.html("""
<script>
    // Scroll to bottom of the Streamlit main content area
    function scrollToBottom() {
        const mainContent = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
        if (mainContent) {
            mainContent.scrollTop = mainContent.scrollHeight;
        }
        // Also try scrolling the body
        window.parent.document.body.scrollTop = window.parent.document.body.scrollHeight;
        window.parent.scrollTo(0, window.parent.document.body.scrollHeight);
    }
    // Small delay to let Streamlit finish rendering
    setTimeout(scrollToBottom, 150);
    setTimeout(scrollToBottom, 400);
</script>
""", height=0)

# ── Smart Pandas engine ───────────────────────────────────────────────────────
def smart_pandas_answer(question: str, df: pd.DataFrame):
    q = question.lower().strip()
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()
    result_df = None
    lines = []

    try:
        if any(w in q for w in ["statistic", "summary", "describe", "overview", "full stat"]):
            result_df = df.describe().round(3)
            lines = [
                f"**Dataset Overview**",
                f"- **Rows:** {df.shape[0]:,} | **Columns:** {df.shape[1]}",
                f"- **Numeric columns:** {len(num_cols)} | **Categorical columns:** {len(cat_cols)}",
                f"- **Total missing values:** {df.isnull().sum().sum():,}",
                f"- **Duplicate rows:** {df.duplicated().sum():,}",
                "", "**Descriptive Statistics:**",
            ]

        elif any(w in q for w in ["missing", "null", "nan", "empty"]):
            miss = df.isnull().sum()
            miss_pct = (df.isnull().mean() * 100).round(2)
            miss_df = pd.DataFrame({"Missing Count": miss, "Missing %": miss_pct})
            miss_df = miss_df[miss_df["Missing Count"] > 0].sort_values("Missing Count", ascending=False)
            if len(miss_df):
                result_df = miss_df
                lines = [f"**Missing Values** in **{len(miss_df)}** of {df.shape[1]} columns:"]
            else:
                lines = ["✅ **No missing values** found. Dataset is complete."]

        elif any(w in q for w in ["correlation", "corr", "relate", "relationship"]):
            if len(num_cols) >= 2:
                corr = df[num_cols].corr().round(3)
                result_df = corr
                pairs = []
                for i in range(len(corr.columns)):
                    for j in range(i+1, len(corr.columns)):
                        pairs.append((corr.columns[i], corr.columns[j], corr.iloc[i,j]))
                pairs.sort(key=lambda x: abs(x[2]), reverse=True)
                top_str = "\n".join([f"  - **{a}** ↔ **{b}**: `{v:.3f}`" for a,b,v in pairs[:3]])
                lines = [f"**Correlation Matrix** ({len(num_cols)} numeric columns):", "", "**Strongest correlations:**", top_str]
            else:
                lines = ["⚠️ Need at least 2 numeric columns."]

        elif any(w in q for w in ["shape","size","dimension","how many row","how many col","rows","columns"]):
            lines = [
                f"**Dataset Shape:**",
                f"- Rows: **{df.shape[0]:,}** | Columns: **{df.shape[1]}**",
                f"- Numeric: {len(num_cols)} cols | Categorical: {len(cat_cols)} cols",
                f"- Total cells: {df.shape[0]*df.shape[1]:,}",
            ]

        elif any(w in q for w in ["top 5","first 5","head","preview","sample"]):
            result_df = df.head(5)
            lines = [f"**First 5 rows:**"]

        elif any(w in q for w in ["unique","distinct","cardinality"]):
            uniq_df = pd.DataFrame({
                "Column": df.columns,
                "Type": df.dtypes.astype(str),
                "Unique Values": df.nunique(),
                "Unique %": (df.nunique()/len(df)*100).round(1)
            }).sort_values("Unique Values", ascending=False)
            result_df = uniq_df
            lines = [f"**Unique Value Counts** ({df.shape[1]} columns):"]

        elif "duplicate" in q:
            n = df.duplicated().sum()
            lines = [f"**Duplicate Rows:** {n:,} ({n/len(df)*100:.2f}% of total)",
                     "✅ No duplicates." if n == 0 else "⚠️ Consider removing duplicates."]

        elif any(w in q for w in ["mean","average","avg"]):
            if num_cols:
                r = df[num_cols].mean().round(4).reset_index()
                r.columns = ["Column","Mean"]
                result_df = r
                lines = ["**Column Means:**"]

        elif any(w in q for w in ["maximum","max","highest","largest"]):
            if num_cols:
                r = df[num_cols].max().reset_index()
                r.columns = ["Column","Maximum"]
                result_df = r
                lines = ["**Maximum Values:**"]

        elif any(w in q for w in ["minimum","min","lowest","smallest"]):
            if num_cols:
                r = df[num_cols].min().reset_index()
                r.columns = ["Column","Minimum"]
                result_df = r
                lines = ["**Minimum Values:**"]

        elif any(w in q for w in ["column","feature","field","list col"]):
            col_df = pd.DataFrame({
                "Column": df.columns,
                "Type": df.dtypes.astype(str),
                "Non-Null": df.notnull().sum(),
                "Null": df.isnull().sum(),
                "Unique": df.nunique()
            })
            result_df = col_df
            lines = [f"**Column Info** ({df.shape[1]} columns):"]

        elif any(w in q for w in ["count","frequency","distribution","most common"]):
            target_col_name = None
            for c in df.columns:
                if c.lower() in q:
                    target_col_name = c
                    break
            if target_col_name is None and cat_cols:
                target_col_name = cat_cols[0]
            if target_col_name:
                vc = df[target_col_name].value_counts().head(15).reset_index()
                vc.columns = [target_col_name,"Count"]
                vc["Percentage"] = (vc["Count"]/len(df)*100).round(2)
                result_df = vc
                lines = [f"**Value Distribution** — `{target_col_name}`:"]

        elif any(w in q for w in ["sum","total"]):
            if num_cols:
                r = df[num_cols].sum().round(4).reset_index()
                r.columns = ["Column","Sum"]
                result_df = r
                lines = ["**Column Totals:**"]

        elif any(w in q for w in ["outlier","anomaly","extreme"]):
            if num_cols:
                rows = []
                for col in num_cols:
                    Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    n_out = len(df[(df[col] < Q1-1.5*IQR) | (df[col] > Q3+1.5*IQR)])
                    rows.append({"Column":col, "Outliers":n_out, "Outlier %":round(n_out/len(df)*100,2),
                                 "Lower":round(Q1-1.5*IQR,3), "Upper":round(Q3+1.5*IQR,3)})
                result_df = pd.DataFrame(rows).sort_values("Outliers",ascending=False)
                lines = ["**Outlier Analysis** (IQR method):"]

        elif any(w in q for w in ["type","dtype","datatype"]):
            result_df = pd.DataFrame({
                "Column": df.columns,
                "Data Type": df.dtypes.astype(str),
                "Non-Null": df.notnull().sum(),
                "Sample": [str(df[c].dropna().iloc[0]) if len(df[c].dropna())>0 else "N/A" for c in df.columns]
            })
            lines = ["**Data Types:**"]

    except Exception as e:
        lines = [f"⚠️ Computation error: {e}"]

    return "\n".join(lines), result_df


# ── Handle input ──────────────────────────────────────────────────────────────
pending  = st.session_state.pop("pending_question", None)
question = st.chat_input("Ask anything about your data…")
if pending and not question:
    question = pending

if question:
    st.session_state["chat_history"].append({"role": "user", "message": question})
    save_message(user["id"], "user", question, upload.get("id"))

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing…"):
            answer = ""

            if ft in ("csv","xlsx","xls") and df is not None:
                pandas_ans, result_df = smart_pandas_answer(question, df)

                if pandas_ans:
                    st.markdown(pandas_ans)
                    if result_df is not None:
                        st.dataframe(result_df, use_container_width=True)

                    # LLM business insight on top
                    provider = get_llm_provider()
                    if provider != "fallback" and df_summary:
                        try:
                            insight = call_llm(
                                f"User asked: '{question}'\nComputed result shown.\nDataset: {df_summary[:600]}\nAdd 2 sentences of specific business insight.",
                                system="Data analyst. Give concise, specific insight. No generic statements.",
                                max_tokens=200
                            )
                            if insight and not insight.startswith("["):
                                st.markdown("---")
                                st.markdown(f"**💡 Insight:** {insight}")
                                answer = pandas_ans + "\n\n💡 " + insight
                            else:
                                answer = pandas_ans
                        except Exception:
                            answer = pandas_ans
                    else:
                        answer = pandas_ans

                else:
                    system = (
                        "You are an expert data analyst. Answer questions about datasets clearly.\n"
                        "Include direct answers, specific numbers, bullet points, bold key findings.\n"
                        "Never say 'I cannot analyze' — use the context to give your best answer."
                    )
                    history_ctx = "\n".join([
                        f"{'User' if m['role']=='user' else 'Assistant'}: {m['message'][:200]}"
                        for m in st.session_state["chat_history"][-6:-1]
                    ])
                    prompt = (
                        f"Dataset summary:\n{df_summary}\n\n"
                        f"Recent conversation:\n{history_ctx}\n\n"
                        f"Question: {question}\n\nAnswer with specific details:"
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
                answer = "⚠️ Could not generate a response. Please check your API key in `.env`."
                st.markdown(answer)

    st.session_state["chat_history"].append({"role": "assistant", "message": answer})
    save_message(user["id"], "assistant", answer, upload.get("id"))

    # Auto-scroll to bottom after new message
    st.components.v1.html("""
    <script>
        function scrollToBottom() {
            const app = window.parent.document.querySelector('[data-testid="stAppViewContainer"]');
            if (app) app.scrollTop = app.scrollHeight;
            window.parent.scrollTo(0, window.parent.document.body.scrollHeight);
        }
        setTimeout(scrollToBottom, 100);
        setTimeout(scrollToBottom, 500);
        setTimeout(scrollToBottom, 1000);
    </script>
    """, height=0)