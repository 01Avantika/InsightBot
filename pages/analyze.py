"""
pages/analyze.py — Upload & Analyze with Exact Sidebar Design
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

# ─────────────────────────────────────────────────────────────────────────────
# EXACT SIDEBAR STYLING FROM IMAGE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Root reset ── */
* { font-family: 'Inter', sans-serif; margin: 0; padding: 0; box-sizing: border-box; }

/* ── Hide Streamlit defaults ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
[data-testid="stSidebarNav"] { display: none !important; }

/* ── Main app background ── */
.stApp {
    background: #0a0a0f;
}

/* ── SIDEBAR: Exact match from image ── */
[data-testid="stSidebar"] {
    background: #16161f !important;
    border-right: 1px solid rgba(88, 80, 236, 0.15) !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

/* ── Logo section (exact styling) ── */
.sidebar-logo {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 24px 20px;
    margin-bottom: 8px;
}

.logo-icon {
    width: 40px;
    height: 40px;
    background: linear-gradient(135deg, #5850EC 0%, #7C3AED 100%);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
}

.logo-text {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.logo-title {
    font-size: 16px;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.3px;
}

.logo-subtitle {
    font-size: 9px;
    font-weight: 600;
    color: #7C3AED;
    letter-spacing: 1.2px;
    text-transform: uppercase;
}

/* ── Navigation links (exact styling from image) ── */
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    padding: 11px 20px !important;
    margin: 0 12px 4px 12px !important;
    border-radius: 8px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #9CA3AF !important;
    text-decoration: none !important;
    transition: all 0.2s ease !important;
    border: none !important;
    background: transparent !important;
}

[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {
    background: rgba(88, 80, 236, 0.08) !important;
    color: #D1D5DB !important;
}

/* Active page (exact purple style from image) */
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"][aria-current="page"] {
    background: linear-gradient(90deg, rgba(88, 80, 236, 0.15) 0%, rgba(88, 80, 236, 0.05) 100%) !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-left: 3px solid #5850EC !important;
    padding-left: 17px !important;
}

/* ── Profile section at bottom (exact styling) ── */
.profile-section {
    position: absolute;
    bottom: 20px;
    left: 12px;
    right: 12px;
}

.profile-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
    background: rgba(88, 80, 236, 0.08);
    border: 1px solid rgba(88, 80, 236, 0.2);
    border-radius: 10px;
    margin-bottom: 12px;
    transition: all 0.2s ease;
}

.profile-card:hover {
    background: rgba(88, 80, 236, 0.12);
    border-color: rgba(88, 80, 236, 0.3);
}

.profile-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #5850EC 0%, #7C3AED 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    font-weight: 700;
    color: #FFFFFF;
    flex-shrink: 0;
}

.profile-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
}

.profile-name {
    font-size: 13px;
    font-weight: 600;
    color: #FFFFFF;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.profile-email {
    font-size: 11px;
    font-weight: 400;
    color: #6B7280;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ── Logout button (exact styling) ── */
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #5850EC 0%, #7C3AED 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 11px 0 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
}

/* ─────── MAIN CONTENT STYLES ─────── */

/* Page title */
.page-title {
    font-size: 28px;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 6px;
    letter-spacing: -0.5px;
}

.page-subtitle {
    font-size: 14px;
    font-weight: 400;
    color: #9CA3AF;
    margin-bottom: 24px;
}

/* Section headers */
.section-header {
    font-size: 16px;
    font-weight: 600;
    color: #FFFFFF;
    margin: 32px 0 16px;
    padding-left: 12px;
    border-left: 3px solid #5850EC;
}

/* Stat boxes */
.stat-box {
    background: linear-gradient(135deg, rgba(88, 80, 236, 0.1) 0%, rgba(124, 58, 237, 0.05) 100%);
    border: 1px solid rgba(88, 80, 236, 0.2);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    transition: all 0.3s ease;
}

.stat-box:hover {
    background: linear-gradient(135deg, rgba(88, 80, 236, 0.15) 0%, rgba(124, 58, 237, 0.08) 100%);
    border-color: rgba(88, 80, 236, 0.35);
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(88, 80, 236, 0.2);
}

.stat-value {
    font-size: 32px;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 11px;
    font-weight: 600;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* File cards */
.file-card {
    background: rgba(88, 80, 236, 0.05);
    border: 1px solid rgba(88, 80, 236, 0.15);
    border-radius: 10px;
    padding: 14px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    transition: all 0.2s ease;
}

.file-card:hover {
    background: rgba(88, 80, 236, 0.08);
    border-color: rgba(88, 80, 236, 0.25);
    transform: translateX(4px);
}

/* File type tags */
.file-tag {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.tag-csv { background: #10B981; color: #FFFFFF; }
.tag-pdf { background: #EF4444; color: #FFFFFF; }
.tag-xlsx { background: #3B82F6; color: #FFFFFF; }
.tag-xls { background: #2563EB; color: #FFFFFF; }

/* AI Cards */
.ai-card {
    background: rgba(88, 80, 236, 0.06);
    border: 1px solid rgba(88, 80, 236, 0.2);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 16px;
    transition: all 0.3s ease;
}

.ai-card:hover {
    background: rgba(88, 80, 236, 0.1);
    border-color: rgba(88, 80, 236, 0.35);
    box-shadow: 0 4px 16px rgba(88, 80, 236, 0.15);
}

.ai-card-title {
    font-size: 14px;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 8px;
}

.ai-card-body {
    font-size: 13px;
    font-weight: 400;
    color: #D1D5DB;
    line-height: 1.6;
}

.ai-card-success {
    background: rgba(16, 185, 129, 0.08);
    border-color: rgba(16, 185, 129, 0.25);
}

.ai-card-warning {
    background: rgba(245, 158, 11, 0.08);
    border-color: rgba(245, 158, 11, 0.25);
}

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 6px;
    margin-top: 6px;
}

.badge-green { background: rgba(16, 185, 129, 0.15); color: #10B981; border: 1px solid rgba(16, 185, 129, 0.3); }
.badge-yellow { background: rgba(245, 158, 11, 0.15); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.3); }
.badge-red { background: rgba(239, 68, 68, 0.15); color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.3); }
.badge-blue { background: rgba(88, 80, 236, 0.15); color: #5850EC; border: 1px solid rgba(88, 80, 236, 0.3); }

/* Buttons */
.main .stButton > button {
    background: linear-gradient(135deg, #5850EC 0%, #7C3AED 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.main .stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(88, 80, 236, 0.3) !important;
}

/* File uploader */
.stFileUploader {
    border: 2px dashed rgba(88, 80, 236, 0.3) !important;
    border-radius: 12px !important;
    background: rgba(88, 80, 236, 0.03) !important;
    padding: 24px !important;
}

.stFileUploader:hover {
    border-color: rgba(88, 80, 236, 0.5) !important;
    background: rgba(88, 80, 236, 0.06) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(88, 80, 236, 0.05);
    padding: 6px;
    border-radius: 10px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 14px;
    color: #9CA3AF;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #5850EC 0%, #7C3AED 100%) !important;
    color: #FFFFFF !important;
}

/* Dataframe */
.stDataFrame {
    border: 1px solid rgba(88, 80, 236, 0.15);
    border-radius: 10px;
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(88, 80, 236, 0.06) !important;
    border: 1px solid rgba(88, 80, 236, 0.15) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    color: #FFFFFF !important;
}

.streamlit-expanderHeader:hover {
    background: rgba(88, 80, 236, 0.1) !important;
    border-color: rgba(88, 80, 236, 0.25) !important;
}

/* Success/Info messages */
.stSuccess {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 8px;
    color: #10B981;
}

.stInfo {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 8px;
    color: #3B82F6;
}

.stWarning {
    background: rgba(245, 158, 11, 0.1);
    border: 1px solid rgba(245, 158, 11, 0.3);
    border-radius: 8px;
    color: #F59E0B;
}

.stError {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 8px;
    color: #EF4444;
}

</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR 
# ─────────────────────────────────────────────────────────────────────────────
u_name = user.get("username", "User")
u_email = user.get("email", "user@example.com")
u_initial = u_name[0].upper() if u_name else "U"

with st.sidebar:
    # Logo (exact styling)
    st.markdown(f"""
    <div class="sidebar-logo">
        <div class="logo-icon">🤖</div>
        <div class="logo-text">
            <div class="logo-title">InsightBot</div>
            <div class="logo-subtitle">AI INTELLIGENCE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation links (exact styling)
    st.page_link("pages/dashboard.py", label="⊞ Dashboard")
    st.page_link("pages/analyze.py", label="☁ Upload & Analyze")
    st.page_link("pages/automl.py", label="⚙️ AutoML")
    st.page_link("pages/chat.py", label="🗨 Chat with Data")
    st.page_link("pages/history.py", label="↺  History")

    # Spacer to push profile to bottom
    for _ in range(12):
        st.markdown("<br>", unsafe_allow_html=True)

    # Profile card (exact styling)
    st.markdown(f"""
    <div class="profile-section">
        <div class="profile-card">
            <div class="profile-avatar">{u_initial}</div>
            <div class="profile-info">
                <div class="profile-name">{u_name}</div>
                <div class="profile-email">{u_email}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Logout button
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/login.py")


# ─────────────────────────────────────────────────────────────────────────────
# AI HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def ai_pre_scan(df: pd.DataFrame) -> dict:
    """Quick heuristic pre-scan for PII, quality issues, and outliers."""
    pii_patterns = ["email", "phone", "ssn", "social", "address", "zip", "postal",
                    "passport", "credit", "card", "dob", "birth", "gender", "sex",
                    "race", "ethnicity", "salary", "income", "national"]
    pii_cols, quality_issues, outlier_cols = [], [], []

    for col in df.columns:
        col_l = col.lower()
        if any(p in col_l for p in pii_patterns):
            pii_cols.append(col)
        null_pct = df[col].isnull().mean()
        if null_pct > 0.30:
            quality_issues.append(f"'{col}' is {null_pct:.0%} empty")
        if df[col].nunique() == 1:
            quality_issues.append(f"'{col}' has only one unique value")

    for col in df.select_dtypes(include="number").columns:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        if iqr > 0:
            outliers = ((df[col] < q1 - 3*iqr) | (df[col] > q3 + 3*iqr)).sum()
            if outliers > 0:
                outlier_cols.append(f"'{col}' ({outliers} extreme points)")

    return {"pii": pii_cols, "quality": quality_issues, "outliers": outlier_cols}


def get_model_suggestion(filename: str, ext: str, df: pd.DataFrame = None) -> dict:
    """Heuristic LLM model recommendation."""
    name_l = filename.lower()
    suggestions = {
        "model": "claude-3-5-sonnet",
        "label": "Claude 3.5 Sonnet",
        "reason": "Balanced reasoning for general data analysis.",
        "icon": "🤖"
    }

    financial_kw = ["finance", "financial", "revenue", "sales", "invoice", "budget", "profit",
                    "loss", "accounting", "payroll", "transaction", "bank", "stock", "price"]
    medical_kw = ["medical", "health", "patient", "clinical", "diagnosis", "hospital",
                  "drug", "dose", "treatment", "icd", "lab", "vitals"]
    nlp_kw = ["text", "review", "feedback", "comment", "sentiment", "tweet", "email",
              "survey", "response", "article", "blog", "description"]
    big_data_kw = ["large", "big", "dataset", "warehouse", "million", "billion"]

    cols_str = " ".join(df.columns.str.lower().tolist()) if df is not None else ""
    combined = name_l + " " + cols_str

    if any(k in combined for k in financial_kw):
        suggestions = {"model": "gpt-4o", "label": "GPT-4o", "icon": "💰",
                       "reason": "Financial data benefits from GPT-4o's deep numeric reasoning and audit-trail explanations."}
    elif any(k in combined for k in medical_kw):
        suggestions = {"model": "claude-3-opus", "label": "Claude 3 Opus", "icon": "🏥",
                       "reason": "Medical datasets need careful, safety-aware analysis — Claude 3 Opus excels here."}
    elif any(k in combined for k in nlp_kw) or ext == "pdf":
        suggestions = {"model": "gemini-1.5-pro", "label": "Gemini 1.5 Pro", "icon": "📝",
                       "reason": "Long-context text and documents are handled superbly by Gemini 1.5 Pro."}
    elif any(k in combined for k in big_data_kw):
        suggestions = {"model": "gpt-4o-mini", "label": "GPT-4o Mini", "icon": "⚡",
                       "reason": "Large datasets need a fast, cost-efficient model — GPT-4o Mini delivers speed without sacrificing insight."}

    return suggestions


def auto_clean_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Apply heuristic auto-cleaning."""
    cleaned = df.copy()
    log = []

    for col in cleaned.columns:
        null_count = cleaned[col].isnull().sum()
        if null_count == 0:
            continue

        if pd.api.types.is_numeric_dtype(cleaned[col]):
            median_val = cleaned[col].median()
            cleaned[col].fillna(median_val, inplace=True)
            log.append(f"Filled **{null_count}** missing values in `{col}` with median ({median_val:.2f})")

        elif pd.api.types.is_object_dtype(cleaned[col]):
            date_kw = ["date", "time", "year", "month", "day", "created", "updated", "timestamp"]
            if any(k in col.lower() for k in date_kw):
                try:
                    cleaned[col] = pd.to_datetime(cleaned[col], errors="coerce")
                    log.append(f"Parsed `{col}` as datetime column")
                    continue
                except Exception:
                    pass
            mode_val = cleaned[col].mode()
            if not mode_val.empty:
                cleaned[col].fillna(mode_val[0], inplace=True)
                log.append(f"Filled **{null_count}** missing values in `{col}` with mode ('{mode_val[0]}')")

    before = len(cleaned)
    cleaned.dropna(how="all", inplace=True)
    dropped = before - len(cleaned)
    if dropped:
        log.append(f"Removed **{dropped}** fully-empty rows")

    dups = cleaned.duplicated().sum()
    if dups:
        cleaned.drop_duplicates(inplace=True)
        log.append(f"Removed **{dups}** duplicate rows")

    return cleaned, log


# ─────────────────────────────────────────────────────────────────────────────
# RENDER ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def render_analysis(file_path, ext, filename, upload_id, prefix=""):
    k = f"{prefix}_{upload_id}"

    if ext in ("csv", "xlsx", "xls"):
        if st.session_state.get("loaded_upload_id") != upload_id:
            df = load_file(file_path, ext)
            st.session_state["current_df"] = df
            st.session_state["current_df_summary"] = get_summary_text(df)
            st.session_state["loaded_upload_id"] = upload_id
            st.session_state.pop("prescan_result", None)
            st.session_state.pop("cleaned_df", None)
            st.session_state.pop("clean_log", None)

        df = st.session_state.get("cleaned_df", st.session_state["current_df"])
        stats = get_basic_stats(df)
        rows, cols_n = stats["shape"]

        # Stat boxes
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-box"><div class="stat-value">{rows:,}</div><div class="stat-label">Rows</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-box"><div class="stat-value">{cols_n}</div><div class="stat-label">Columns</div></div>', unsafe_allow_html=True)
        with c3:
            miss = sum(stats["missing"].values())
            st.markdown(f'<div class="stat-box"><div class="stat-value">{miss}</div><div class="stat-label">Missing</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="stat-box"><div class="stat-value">{stats["duplicates"]}</div><div class="stat-label">Duplicates</div></div>', unsafe_allow_html=True)

        # AI Pre-Analysis
        st.markdown('<div class="section-header">🔬 AI Pre-Analysis</div>', unsafe_allow_html=True)

        prescan_col, suggest_col = st.columns([1, 1])

        with prescan_col:
            run_prescan = st.toggle(
                "Enable AI Pre-Scan (PII / Quality / Outliers)",
                value=st.session_state.get(f"prescan_on_{k}", False),
                key=f"prescan_toggle_{k}"
            )
            st.session_state[f"prescan_on_{k}"] = run_prescan

            if run_prescan:
                if st.session_state.get("prescan_result") is None:
                    with st.spinner("🔍 Scanning dataset…"):
                        result = ai_pre_scan(df)
                        st.session_state["prescan_result"] = result
                else:
                    result = st.session_state["prescan_result"]

                pii = result["pii"]
                qual = result["quality"]
                outl = result["outliers"]
                all_clear = not pii and not qual and not outl

                badges = ""
                if all_clear:
                    badges = '<span class="badge badge-green">✅ All Clear</span>'
                else:
                    if pii:
                        badges += f'<span class="badge badge-red">🔐 {len(pii)} PII Col{"s" if len(pii)>1 else ""}</span>'
                    if qual:
                        badges += f'<span class="badge badge-yellow">⚠️ {len(qual)} Quality Issue{"s" if len(qual)>1 else ""}</span>'
                    if outl:
                        badges += f'<span class="badge badge-blue">📊 {len(outl)} Outlier Col{"s" if len(outl)>1 else ""}</span>'

                body_lines = []
                if pii:
                    body_lines.append(f"<b>PII detected:</b> {', '.join(f'<code>{c}</code>' for c in pii)}")
                if qual:
                    body_lines += [f"• {q}" for q in qual]
                if outl:
                    body_lines += [f"• Outliers in {o}" for o in outl]
                if all_clear:
                    body_lines.append("No sensitive data, quality issues, or outliers detected.")

                body = "<br>".join(body_lines)
                st.markdown(f"""
                <div class="ai-card ai-card-success">
                    <div class="ai-card-title">🛡️ Pre-Scan Results</div>
                    <div>{badges}</div>
                    <div class="ai-card-body" style="margin-top:10px">{body}</div>
                </div>
                """, unsafe_allow_html=True)

        with suggest_col:
            suggestion = get_model_suggestion(filename, ext, df)
            st.markdown(f"""
            <div class="ai-card">
                <div class="ai-card-title">🤖 AI Model Recommendation</div>
                <div class="ai-card-body">
                    <div style="font-size:22px;margin:8px 0">{suggestion['icon']} <b style="color:#5850EC">{suggestion['label']}</b></div>
                    {suggestion['reason']}
                    <div style="margin-top:10px">
                        <span class="badge badge-blue">Model: {suggestion['model']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # AI Auto-Clean
        st.markdown('<div class="section-header">🧹 AI Auto-Clean Assistant</div>', unsafe_allow_html=True)

        clean_col1, clean_col2 = st.columns([3, 1])
        with clean_col1:
            miss_total = df.isnull().sum().sum()
            dups_total = df.duplicated().sum()
            st.markdown(
                f"<p style='color:#9CA3AF;font-size:13px'>Dataset has "
                f"<b style='color:#F59E0B'>{miss_total:,}</b> missing values and "
                f"<b style='color:#F59E0B'>{dups_total:,}</b> duplicate rows. "
                f"Auto-Clean will fill nulls (median/mode), parse dates, and remove duplicates.</p>",
                unsafe_allow_html=True
            )
        with clean_col2:
            if st.button("🧹 Auto-Clean Data", key=f"autoclean_btn_{k}"):
                with st.spinner("Cleaning…"):
                    cleaned_df, log = auto_clean_dataframe(df)
                    st.session_state["cleaned_df"] = cleaned_df
                    st.session_state["clean_log"] = log
                    st.session_state["current_df_summary"] = get_summary_text(cleaned_df)
                    st.rerun()

        if st.session_state.get("clean_log"):
            with st.expander("✅ Auto-Clean Report", expanded=True):
                for entry in st.session_state["clean_log"]:
                    st.markdown(f"- {entry}")
            if st.button("↩️ Undo Cleaning", key=f"undo_clean_{k}"):
                st.session_state.pop("cleaned_df", None)
                st.session_state.pop("clean_log", None)
                st.rerun()

        # Data Preview
        st.markdown('<div class="section-header">👁️ Data Preview</div>', unsafe_allow_html=True)
        st.dataframe(df.head(50), use_container_width=True, height=300)

        with st.expander("📋 Column Details"):
            col_info = pd.DataFrame({
                "Column": df.columns,
                "Type": df.dtypes.astype(str),
                "Non-Null": df.notnull().sum(),
                "Null %": (df.isnull().mean()*100).round(1),
                "Unique": df.nunique(),
            })
            st.dataframe(col_info, use_container_width=True)

        with st.expander("📈 Descriptive Statistics"):
            num_df = df.select_dtypes(include="number")
            if not num_df.empty:
                st.dataframe(num_df.describe().round(3), use_container_width=True)
            else:
                st.info("No numeric columns found.")

        # Auto Charts
        st.markdown('<div class="section-header">📊 Auto-Generated Visualizations</div>', unsafe_allow_html=True)
        charts = auto_generate_charts(df)
        for i in range(0, len(charts), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(charts):
                    title, fig = charts[i + j]
                    with col:
                        st.plotly_chart(fig, use_container_width=True, key=f"auto_chart_{k}_{i}_{j}")

        # Custom Chart
        st.markdown('<div class="section-header">🎨 Custom Chart Builder</div>', unsafe_allow_html=True)
        num_cols = df.select_dtypes(include="number").columns.tolist()
        all_cols = df.columns.tolist()
        cc1, cc2, cc3, cc4 = st.columns(4)
        with cc1: chart_type = st.selectbox("Chart Type", ["Scatter", "Bar", "Line", "Histogram", "Box", "Pie"], key=f"ct_{k}")
        with cc2: x_col = st.selectbox("X Axis", all_cols, key=f"xc_{k}")
        with cc3: y_col = st.selectbox("Y Axis", num_cols if num_cols else all_cols, key=f"yc_{k}")
        with cc4: color_col = st.selectbox("Color By", ["None"] + all_cols, key=f"cc_{k}")

        if st.button("🎨 Generate Chart", key=f"chart_btn_{k}"):
            import plotly.express as px
            color = None if color_col == "None" else color_col
            try:
                if chart_type == "Scatter": fig = px.scatter(df, x=x_col, y=y_col, color=color, opacity=0.6)
                elif chart_type == "Bar": fig = px.bar(df, x=x_col, y=y_col, color=color)
                elif chart_type == "Line": fig = px.line(df, x=x_col, y=y_col, color=color)
                elif chart_type == "Histogram": fig = px.histogram(df, x=x_col, color=color)
                elif chart_type == "Box": fig = px.box(df, x=color, y=y_col)
                elif chart_type == "Pie":
                    vc = df[x_col].value_counts().head(10)
                    fig = px.pie(values=vc.values, names=vc.index, title=f"{x_col} Distribution")
                fig.update_layout(height=420)
                st.plotly_chart(fig, use_container_width=True, key=f"custom_chart_{k}")
            except Exception as e:
                st.error(f"Chart error: {e}")

        # AI Insights
        st.markdown('<div class="section-header">🧠 AI-Generated Insights</div>', unsafe_allow_html=True)
        if st.button("✨ Generate AI Insights", type="primary", key=f"insights_btn_{k}"):
            with st.spinner("🤖 Analyzing your dataset…"):
                summary = get_summary_text(df)
                insights = generate_insights(summary, filename)
                save_analysis(user["id"], upload_id, summary, insights)
                st.session_state["last_insights"] = insights

        if st.session_state.get("last_insights"):
            st.markdown(st.session_state["last_insights"])
            if st.button("💬 Chat About This Data", key=f"goto_chat_{k}"):
                st.switch_page("pages/chat.py")

    # PDF
    elif ext == "pdf":
        if st.session_state.get("loaded_upload_id") != upload_id:
            with st.spinner("Extracting PDF content…"):
                pdf_text = extract_pdf_text(file_path)
                st.session_state["current_pdf_text"] = pdf_text
                st.session_state["current_pdf_path"] = file_path
                st.session_state["loaded_upload_id"] = upload_id

        pages = get_pdf_page_count(file_path)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="stat-box"><div class="stat-value">{pages}</div><div class="stat-label">Pages</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-box"><div class="stat-value">{format_file_size(os.path.getsize(file_path))}</div><div class="stat-label">File Size</div></div>', unsafe_allow_html=True)

        suggestion = get_model_suggestion(filename, "pdf")
        st.markdown(f"""
        <div class="ai-card" style="margin-top:20px">
            <div class="ai-card-title">🤖 AI Model Recommendation</div>
            <div class="ai-card-body">
                <div style="font-size:22px;margin:8px 0">{suggestion['icon']} <b style="color:#5850EC">{suggestion['label']}</b></div>
                {suggestion['reason']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("📄 View Extracted Text", expanded=False):
            st.text(st.session_state.get("current_pdf_text", "")[:3000])

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
                    f"Summarize this document:\n\n{st.session_state.get('current_pdf_text', '')[:4000]}",
                    system="You are an expert document analyst. Provide a clear, structured summary.",
                )
                save_analysis(user["id"], upload_id, "PDF text preview", summary)
                st.markdown(summary)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN PAGE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">📁 Upload & Analyze</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Upload a new file or resume working on a previous one</div>', unsafe_allow_html=True)

tab_new, tab_resume = st.tabs(["📤 Upload New File", "📂 Resume Previous File"])

# TAB 1 — Upload New File
with tab_new:
    col_up, col_ai = st.columns([3, 1])

    with col_up:
        uploaded = st.file_uploader(
            "Drop your file here or click to browse",
            type=["csv", "xlsx", "xls", "pdf"],
            key="file_uploader"
        )

    with col_ai:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
        if uploaded:
            st.markdown("""
            <div class="ai-card ai-card-success" style="padding:12px 16px">
                <div class="ai-card-title" style="font-size:12px;margin-bottom:4px">🟢 File Received</div>
                <div class="ai-card-body" style="font-size:11px">Pre-scan available after loading.</div>
            </div>
            """, unsafe_allow_html=True)

    if uploaded:
        file_key = f"{uploaded.name}_{uploaded.size}"
        if st.session_state.get("last_uploaded_key") != file_key:
            file_bytes = uploaded.read()
            ext = get_file_extension(uploaded.name)
            file_path, file_size = save_uploaded_file(file_bytes, uploaded.name, user["id"])
            upload_id = save_upload(user["id"], uploaded.name, ext, file_path, file_size)
            st.session_state["current_upload"] = {"id": upload_id, "filename": uploaded.name, "file_type": ext, "file_path": file_path}
            st.session_state["last_uploaded_key"] = file_key
            st.session_state["loaded_upload_id"] = None
            st.session_state["last_insights"] = None
            st.session_state["chat_history"] = []
            st.session_state.pop("prescan_result", None)
            st.session_state.pop("cleaned_df", None)
            st.session_state.pop("clean_log", None)
            st.success(f"✅ **{uploaded.name}** uploaded! ({format_file_size(uploaded.size)})")

        upload = st.session_state.get("current_upload", {})
        if upload:
            st.markdown(f'<div class="section-header">📊 Analysis — {upload["filename"]}</div>', unsafe_allow_html=True)
            render_analysis(upload["file_path"], upload["file_type"], upload["filename"], upload["id"], prefix="new")

# TAB 2 — Resume Previous File
with tab_resume:
    st.markdown('<div class="section-header">📂 Your Previous Files</div>', unsafe_allow_html=True)
    prev_uploads = get_user_uploads(user["id"])

    if not prev_uploads:
        st.info("No previous files found. Upload a file first.")
    else:
        st.markdown("<p style='color:#9CA3AF;font-size:13px;margin-bottom:20px'>Load to resume analysis · Delete to remove permanently</p>", unsafe_allow_html=True)

        for u in prev_uploads:
            ext = u["file_type"]
            tag_cls = f"tag-{ext}" if ext in ("csv", "pdf", "xlsx", "xls") else "tag-csv"
            col1, col2, col3 = st.columns([5, 1, 1])

            with col1:
                st.markdown(f"""
                <div class="file-card">
                    <span class="file-tag {tag_cls}">{ext.upper()}</span>
                    <b style='color:#FFFFFF;font-size:14px'>{u['filename']}</b>
                    <span style='color:#6B7280;font-size:12px;margin-left:auto'>{u['uploaded_at'][:16]} · {format_file_size(u.get('file_size', 0))}</span>
                </div>""", unsafe_allow_html=True)

            with col2:
                if st.button("▶ Load", key=f"load_{u['id']}"):
                    if os.path.exists(u["file_path"]):
                        st.session_state["current_upload"] = {"id": u["id"], "filename": u["filename"], "file_type": u["file_type"], "file_path": u["file_path"]}
                        st.session_state["loaded_upload_id"] = None
                        st.session_state["last_insights"] = None
                        st.session_state["chat_history"] = []
                        st.session_state.pop("prescan_result", None)
                        st.session_state.pop("cleaned_df", None)
                        st.session_state.pop("clean_log", None)
                        st.success(f"✅ Loaded **{u['filename']}**")
                        st.rerun()
                    else:
                        st.error("File missing on disk. Please re-upload.")

            with col3:
                if st.button("🗑️", key=f"del_{u['id']}", help="Delete this file"):
                    try:
                        if os.path.exists(u["file_path"]):
                            os.remove(u["file_path"])
                    except Exception:
                        pass
                    import sqlite3
                    from db.database import get_connection
                    conn = get_connection()
                    conn.execute("DELETE FROM uploads WHERE id = ?", (u["id"],))
                    conn.execute("DELETE FROM analyses WHERE upload_id = ?", (u["id"],))
                    conn.execute("DELETE FROM chats WHERE upload_id = ?", (u["id"],))
                    conn.commit()
                    conn.close()
                    if st.session_state.get("current_upload", {}).get("id") == u["id"]:
                        st.session_state.pop("current_upload", None)
                        st.session_state.pop("current_df", None)
                        st.session_state.pop("loaded_upload_id", None)
                    st.success(f"🗑️ Deleted **{u['filename']}**")
                    st.rerun()

        upload = st.session_state.get("current_upload", {})
        if upload and os.path.exists(upload.get("file_path", "")):
            if any(u["id"] == upload["id"] for u in prev_uploads):
                st.markdown(f'<div class="section-header">📊 Resuming — {upload["filename"]}</div>', unsafe_allow_html=True)
                render_analysis(upload["file_path"], upload["file_type"], upload["filename"], upload["id"], prefix="resume")