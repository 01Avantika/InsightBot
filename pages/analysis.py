import streamlit as st
from eda import stats
from utils.file_loader import load_file
from eda.summary import generate_summary
from eda.missing import missing_values
from eda.stats import numeric_stats
from eda.explain import explain_stats
from utils.report_generator import generate_report

st.set_page_config(
    page_title="EDA Dashboard",
    layout="wide"
)


st.title("AI-Powered Intelligent Data Analysis System")
st.write("Upload your data and get automatic insights")
uploaded_file = st.file_uploader(
    "Upload CSV or Excel file",
    type=["csv", "xlsx"]
)
show_explanation = st.checkbox(" Show plain-English explanations")
if st.button("Report"):
    st.switch_page("pages/main.py")

if uploaded_file:
    df,file_type = load_file(uploaded_file)
    
    if df is not None:
        st.success(f"{file_type.upper()} file loaded successfully")
        st.write("Data Preview:")
        st.write(df.head())
    else:
        st.error("Unsupported file format")

st.subheader("📂 Exploratory Data Analysis")
# tab,tab1, tab2, tab3 = st.tabs([
#     "Choose",
#     "Summary",
#     "Missing Values",
#     "Statistical Insights"
# ])
# with tab:
#     st.write("choose any")
# with tab1:
#     st.write(generate_summary(df))
# with tab2:
#     st.write(missing_values(df))
# with tab3:
#     st.json(numeric_stats(df))
#     if show_explanation:
#         st.markdown("### Explanation")
#         for line in explain_stats(stats):
#             st.write(line)



eda_option = st.selectbox(
    "Choose EDA option",
    (   "choose",
        "Data Summary",
        "Missing Values",
        "Statistical Insights",
        "Show All"
    )
)
if eda_option == "choose":
    st.subheader("waiting")
    
elif eda_option == "Data Summary":
    st.subheader("📊 Data Summary")
    st.write(generate_summary(df))

elif eda_option == "Missing Values":
    st.subheader("🧹 Missing Values Report")
    st.write(missing_values(df))

elif eda_option == "Statistical Insights":
    st.subheader("📈 Statistical Insights")
    st.json(numeric_stats(df))

elif eda_option == "Show All":
    st.subheader("📊 Data Summary")
    st.write(generate_summary(df))

    st.subheader("🧹 Missing Values Report")
    st.write(missing_values(df))

    st.subheader("📈 Statistical Insights")
    st.json(numeric_stats(df))

report_text = generate_report(
    generate_summary(df),
    missing_values(df),
    numeric_stats(df)
)

st.download_button(
    label="Download EDA Report",
    data=report_text,
    file_name="eda_report.txt",
    mime="text/plain"
)