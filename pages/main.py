import streamlit as st
from utils.file_loader import load_file

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="AI Data & Document Analysis",
    page_icon="📊",
    layout="wide"
)

# ------------------ HEADER ------------------
st.title("🤖 AI-Powered Data & Document Analysis")
st.write(
    "Upload **CSV, Excel, or PDF** files, ask questions in natural language, "
    "and get instant insights, trends, and reports."
)

st.divider()

# ------------------ SIDEBAR ------------------
st.sidebar.header("📁 Upload Files")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV / Excel / PDF",
    type=["csv", "xlsx", "pdf"]
)

file_type = None
data = None

if uploaded_file:
    data, file_type = load_file(uploaded_file)
    st.sidebar.success(f"Detected file type: {file_type.upper()}")

st.sidebar.divider()
st.sidebar.info("Built with Streamlit + LangChain")

# ------------------ MAIN CONTENT ------------------
if uploaded_file:

    tabs = st.tabs([
        "📊 EDA",
        "📈 Trends",
        "🤖 Ask AI",
        "📄 Report"
    ])

    # ------------------ TAB 1: EDA ------------------
    with tabs[0]:
        st.subheader("Exploratory Data Analysis")

        if file_type in ["csv", "excel"]:
            st.dataframe(data, use_container_width=True)
        else:
            st.warning("EDA is available only for structured data (CSV / Excel).")

    # ------------------ TAB 2: TRENDS ------------------
    with tabs[1]:
        st.subheader("Trend Detection & Visualizations")

        if file_type in ["csv", "excel"]:
            st.info("Charts will appear here")
            # placeholder chart
            st.line_chart(data.select_dtypes(include="number"))
        else:
            st.warning("Trend analysis not applicable for PDFs.")

    # ------------------ TAB 3: ASK AI ------------------
    with tabs[2]:
        st.subheader("Ask Questions in Natural Language")

        query = st.text_input(
            "Example: Show sales trend for last quarter"
        )

        if query:
            with st.chat_message("user"):
                st.write(query)

            with st.chat_message("assistant"):
                st.write("🤖 AI response will appear here")

    # ------------------ TAB 4: REPORT ------------------
    with tabs[3]:
        st.subheader("Insight & Report Generation")

        st.write("Executive-level insights and summaries")

        if st.button("Generate Report"):
            st.success("Report generated successfully!")

            report_text = """
            📌 Key Insights:
            - Sales increased by 18%
            - Region A outperformed others
            - Strong upward trend detected
            """

            st.text_area("Generated Report", report_text, height=200)

            st.download_button(
                label="📥 Download Report",
                data=report_text,
                file_name="ai_insights_report.txt"
            )

else:
    st.info("👈 Upload a file from the sidebar to begin analysis")
