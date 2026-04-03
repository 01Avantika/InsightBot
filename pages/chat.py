"""
pages/chat.py — Conversational Q&A for data and documents + Adaptive Theme
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


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

# ---------------- ADAPTIVE CUSTOM CSS (Light/Dark Mode Fix) ----------------
st.markdown("""
<style>
    /* HIDE DEFAULT STREAMLIT NAV */
    [data-testid="stSidebarNav"] {display: none;}

    /* CHAT BUBBLES - Adaptive */
    .chat-bubble-user {
        background: linear-gradient(135deg, #7c3aed, #6d28d9);
        color: white !important; border-radius: 18px 18px 4px 18px;
        padding: 0.75rem 1.1rem; margin: 0.4rem 0;
        max-width: 75%; margin-left: auto;
    }
    .chat-bubble-ai {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(124, 58, 237, 0.2);
        color: var(--text-color); border-radius: 18px 18px 18px 4px;
        padding: 0.75rem 1.1rem; margin: 0.4rem 0; max-width: 80%;
    }
    
    /* CONTEXT BADGE */
    .context-badge {
        background-color: var(--secondary-background-color); 
        border: 1px solid rgba(124, 58, 237, 0.3);
        border-radius: 8px; padding: 0.5rem 1rem; margin-bottom: 1rem; font-size: 0.9rem;
        color: var(--text-color);
    }

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
    
    st.divider()
    
    if upload:
        ft = upload.get("file_type","")
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

    st.markdown("<div style='flex-grow: 1; height: 50px;'></div>", unsafe_allow_html=True)
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

    if st.button("Logout", use_container_width=True, key="logout_btn"):
        st.session_state.clear()
        st.switch_page("pages/login.py")

# ---------------- MAIN CONTENT ----------------
st.markdown("# 💬 Chat with Your Data")

if not upload:
    st.warning("⚠️ No file loaded. Please upload a file first.")
    if st.button("📁 Go to Upload"):
        st.switch_page("pages/analyze.py")
    st.stop()

ft   = upload.get("file_type","")
icon = "📊" if ft in ("csv","xlsx","xls") else "📄"
mode = "Data Analysis" if ft in ("csv","xlsx","xls") else "Document Q&A"
st.markdown(f"""<div class="context-badge">
    {icon} <b>{upload['filename']}</b> &nbsp;·&nbsp; Mode: <b>{mode}</b>
    {'&nbsp;·&nbsp; 🔍 FAISS Indexed' if vectorstore else ''}
</div>""", unsafe_allow_html=True)

# Load persisted chat history on first load
if "chat_history" not in st.session_state:
    persisted = get_user_chats(user["id"], upload.get("id"))
    st.session_state["chat_history"] = [{"role": m["role"], "message": m["message"]} for m in persisted]

# Suggestion chips
if ft in ("csv","xlsx","xls"):
    suggestions = ["What are the key statistics?", "Any missing values?", "Show correlation analysis", "Describe the dataset"]
else:
    suggestions = ["Summarize this document", "What are the main topics?", "List key findings", "What conclusions are drawn?"]

st.markdown("**💡 Quick Questions:**")
cols = st.columns(4)
for i, sug in enumerate(suggestions):
    if cols[i].button(sug, key=f"sug_{i}"):
        st.session_state["prefill_question"] = sug

# Display chat history
for msg in st.session_state["chat_history"]:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user">👤 {msg["message"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-ai">🤖 {msg["message"]}</div>', unsafe_allow_html=True)

prefill  = st.session_state.pop("prefill_question", "")
question = st.chat_input("Ask anything about your data…")
if not question and prefill:
    question = prefill

if question:
    st.session_state["chat_history"].append({"role": "user", "message": question})
    save_message(user["id"], "user", question, upload.get("id"))

    with st.spinner("🤖 Thinking…"):
        answer = ""

        if ft in ("csv","xlsx","xls") and df is not None:
            pandas_answer, result_df = pandas_query(df, question)
            if pandas_answer:
                answer = pandas_answer
                if result_df is not None:
                    st.dataframe(result_df, use_container_width=True)
            else:
                answer = answer_data_question(question, df_summary, st.session_state["chat_history"][:-1])

        elif ft == "pdf":
            if vectorstore:
                answer = answer_pdf_question(question, vectorstore, st.session_state["chat_history"][:-1])
            else:
                from utils.llm import call_llm
                answer = call_llm(
                    f"Based on this document:\n{pdf_text[:4000]}\n\nAnswer: {question}",
                    system="You are a helpful document assistant.",
                )

        if not answer:
            answer = "I couldn't generate a response. Please check your API key configuration."

    st.session_state["chat_history"].append({"role": "assistant", "message": answer})
    save_message(user["id"], "assistant", answer, upload.get("id"))
    st.rerun()
