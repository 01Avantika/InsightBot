"""
pages/automl.py — AutoML: Automated Machine Learning + Predictive Analysis
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

# Models
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.svm import SVC, SVR
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    mean_squared_error, r2_score, mean_absolute_error,
    precision_score, recall_score, f1_score
)

from db.database import init_db, save_analysis
from utils.llm import call_llm, get_llm_provider

init_db()

st.set_page_config(page_title="InsightBot — AutoML", page_icon="🤖", layout="wide")

if not st.session_state.get("user"):
    st.warning("Please login first.")
    st.switch_page("pages/login.py")

user   = st.session_state["user"]
upload = st.session_state.get("current_upload", {})
df     = st.session_state.get("current_df")

st.markdown("""
<style>
    [data-testid="stSidebarNav"] { display: none; }
    .section-header {
        font-size: 1.15rem; font-weight: 700;
        border-left: 4px solid #7c3aed;
        padding-left: 0.75rem; margin: 1.8rem 0 1rem;
    }
    .metric-pill {
        background: rgba(124,58,237,0.1);
        border: 1px solid rgba(124,58,237,0.25);
        border-radius: 12px; padding: 1.2rem;
        text-align: center;
    }
    .pill-val { font-size: 1.8rem; font-weight: 800; color: #a78bfa; }
    .pill-lbl { font-size: 0.75rem; opacity: 0.7; margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.05em; }
    .model-row {
        background: rgba(124,58,237,0.05);
        border: 1px solid rgba(124,58,237,0.12);
        border-radius: 10px; padding: 0.8rem 1rem; margin-bottom: 0.5rem;
        display: flex; justify-content: space-between; align-items: center;
    }
    .best-badge {
        background: linear-gradient(135deg,#7c3aed,#a78bfa);
        color: white; border-radius: 20px;
        padding: 0.2rem 0.7rem; font-size: 0.72rem; font-weight: 700;
    }
    .insight-box {
        background: rgba(124,58,237,0.06);
        border: 1px solid rgba(124,58,237,0.2);
        border-radius: 14px; padding: 1.5rem;
        margin-top: 1rem;
    }
    .user-profile-footer {
        display:flex; align-items:center; gap:12px; padding:12px;
        border-radius:12px; background-color:var(--secondary-background-color);
        border:1px solid rgba(124,58,237,0.2); margin-top:10px;
    }
    .user-avatar {
        width:40px; height:40px; background-color:#7c3aed; color:white!important;
        border-radius:50%; display:flex; align-items:center; justify-content:center;
        font-weight:700; font-size:1.1rem; flex-shrink:0;
    }
    .user-name  { font-weight:600; font-size:0.9rem; }
    .user-email { font-size:0.75rem; opacity:0.6; }
    div.stButton > button {
        background: linear-gradient(135deg,#7c3aed,#a78bfa) !important;
        color: white !important; border: none !important;
        border-radius: 10px !important; font-weight: 600 !important;
    }
    div[data-testid="stSelectbox"] label { font-weight: 600; }
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

    if df is not None:
        st.success(f"📊 {df.shape[0]:,} rows × {df.shape[1]} cols")
        if upload:
            st.caption(f"File: `{upload.get('filename','')}`")
    else:
        st.warning("No dataset loaded.\nGo to Upload & Analyze first.")

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
    if st.button("Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/login.py")

# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("# 🧬 AutoML — Automated Machine Learning")
st.markdown("<p style='opacity:0.7'>Train multiple models automatically, compare performance, and get AI-powered predictions and explanations.</p>", unsafe_allow_html=True)

if df is None:
    st.warning("⚠️ No dataset loaded. Please upload a CSV or Excel file in Upload & Analyze first.")
    if st.button("📁 Go to Upload & Analyze"):
        st.switch_page("pages/analyze.py")
    st.stop()

# ── Step 1: Configure ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Step 1 — Configure Your Model</div>', unsafe_allow_html=True)

col_cfg1, col_cfg2, col_cfg3 = st.columns(3)

with col_cfg1:
    target_col = st.selectbox(
        "🎯 Select Target Column (what to predict)",
        options=df.columns.tolist(),
        index=len(df.columns)-1,
        help="The column you want the model to learn to predict"
    )

with col_cfg2:
    test_size = st.slider("📊 Test Set Size", 0.1, 0.4, 0.2, 0.05,
                          help="Fraction of data held out for testing")

with col_cfg3:
    task_auto = "Classification" if df[target_col].nunique() <= 20 and df[target_col].dtype in ["object","bool","category"] or df[target_col].nunique() <= 10 else "Regression"
    task = st.selectbox("🔧 Task Type", ["Auto-Detect", "Classification", "Regression"],
                        index=0, help="Auto-Detect picks based on target column type")
    if task == "Auto-Detect":
        task = task_auto
        st.caption(f"Auto-detected: **{task}**")

# Feature selection
all_feat_cols = [c for c in df.columns if c != target_col]
selected_features = st.multiselect(
    "📋 Select Feature Columns (leave empty to use all)",
    options=all_feat_cols,
    default=[],
    help="Select specific features or leave empty to use all columns"
)
feature_cols = selected_features if selected_features else all_feat_cols

# Show config summary
cfg1, cfg2, cfg3, cfg4 = st.columns(4)
with cfg1: st.metric("Target", target_col)
with cfg2: st.metric("Task", task)
with cfg3: st.metric("Features", len(feature_cols))
with cfg4: st.metric("Train/Test", f"{int((1-test_size)*100)}/{int(test_size*100)}")

# ── Step 2: Run AutoML ────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Step 2 — Run AutoML</div>', unsafe_allow_html=True)

run_col, _ = st.columns([1, 3])
with run_col:
    run_btn = st.button("🚀 Run AutoML", type="primary", use_container_width=True)

if run_btn:
    with st.spinner("🤖 Training models… this may take a moment"):

        # ── Preprocessing ──────────────────────────────────────────────────
        X = df[feature_cols].copy()
        y = df[target_col].copy()

        # Drop rows where target is null
        mask = y.notna()
        X = X[mask]
        y = y[mask]

        # Encode target for classification
        le = LabelEncoder()
        if task == "Classification":
            y = le.fit_transform(y.astype(str))
            class_names = le.classes_
        else:
            y = pd.to_numeric(y, errors="coerce")
            mask2 = y.notna()
            X = X[mask2]
            y = y[mask2]
            class_names = None

        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42,
            stratify=y if task=="Classification" and len(np.unique(y)) > 1 else None
        )

        # Build preprocessor
        num_features  = X.select_dtypes(include=np.number).columns.tolist()
        cat_features  = X.select_dtypes(exclude=np.number).columns.tolist()

        num_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler",  StandardScaler())
        ])
        cat_transformer = Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])

        preprocessor = ColumnTransformer(transformers=[
            ("num", num_transformer, num_features),
            ("cat", cat_transformer, cat_features),
        ], remainder="drop")

        # ── Model zoo ─────────────────────────────────────────────────────
        if task == "Classification":
            models = {
                "Logistic Regression":    LogisticRegression(max_iter=500, random_state=42),
                "Decision Tree":          DecisionTreeClassifier(random_state=42),
                "Random Forest":          RandomForestClassifier(n_estimators=100, random_state=42),
                "Gradient Boosting":      GradientBoostingClassifier(n_estimators=100, random_state=42),
                "K-Nearest Neighbors":    KNeighborsClassifier(n_neighbors=5),
            }
            metric_name = "Accuracy"
        else:
            models = {
                "Linear Regression":      LinearRegression(),
                "Ridge Regression":       Ridge(alpha=1.0),
                "Decision Tree":          DecisionTreeRegressor(random_state=42),
                "Random Forest":          RandomForestRegressor(n_estimators=100, random_state=42),
                "Gradient Boosting":      GradientBoostingRegressor(n_estimators=100, random_state=42),
            }
            metric_name = "R² Score"

        # ── Train & evaluate ───────────────────────────────────────────────
        results = []
        trained_models = {}

        progress = st.progress(0, text="Training models…")
        for idx, (name, model) in enumerate(models.items()):
            try:
                pipe = Pipeline([("preprocessor", preprocessor), ("model", model)])
                pipe.fit(X_train, y_train)
                y_pred = pipe.predict(X_test)

                if task == "Classification":
                    acc  = accuracy_score(y_test, y_pred)
                    prec = precision_score(y_test, y_pred, average="weighted", zero_division=0)
                    rec  = recall_score(y_test, y_pred, average="weighted", zero_division=0)
                    f1   = f1_score(y_test, y_pred, average="weighted", zero_division=0)
                    cv   = cross_val_score(pipe, X, y, cv=3, scoring="accuracy").mean()
                    results.append({
                        "Model": name, "Accuracy": round(acc,4),
                        "Precision": round(prec,4), "Recall": round(rec,4),
                        "F1 Score": round(f1,4), "CV Score": round(cv,4)
                    })
                else:
                    r2   = r2_score(y_test, y_pred)
                    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                    mae  = mean_absolute_error(y_test, y_pred)
                    cv   = cross_val_score(pipe, X, y, cv=3, scoring="r2").mean()
                    results.append({
                        "Model": name, "R² Score": round(r2,4),
                        "RMSE": round(rmse,4), "MAE": round(mae,4),
                        "CV Score": round(cv,4)
                    })

                trained_models[name] = pipe
            except Exception as e:
                results.append({"Model": name, metric_name: 0, "Error": str(e)})

            progress.progress((idx+1)/len(models), text=f"Trained: {name}")

        progress.empty()

        results_df = pd.DataFrame(results)
        sort_col   = "Accuracy" if task == "Classification" else "R² Score"
        results_df = results_df.sort_values(sort_col, ascending=False).reset_index(drop=True)
        best_model_name = results_df.iloc[0]["Model"]
        best_score      = results_df.iloc[0][sort_col]
        best_pipe       = trained_models[best_model_name]

        # Store in session
        st.session_state["automl_results"]    = results_df
        st.session_state["automl_best_name"]  = best_model_name
        st.session_state["automl_best_score"] = best_score
        st.session_state["automl_best_pipe"]  = best_pipe
        st.session_state["automl_task"]       = task
        st.session_state["automl_target"]     = target_col
        st.session_state["automl_features"]   = feature_cols
        st.session_state["automl_class_names"]= class_names
        st.session_state["automl_X_test"]     = X_test
        st.session_state["automl_y_test"]     = y_test
        st.session_state["automl_num_features"]= num_features
        st.session_state["automl_cat_features"]= cat_features
        st.session_state["automl_le"]         = le if task == "Classification" else None

        st.success(f"✅ AutoML complete! Best model: **{best_model_name}** ({sort_col}: {best_score:.4f})")
        st.rerun()

# ── Step 3: Results ───────────────────────────────────────────────────────────
if st.session_state.get("automl_results") is not None:
    results_df    = st.session_state["automl_results"]
    best_name     = st.session_state["automl_best_name"]
    best_score    = st.session_state["automl_best_score"]
    best_pipe     = st.session_state["automl_best_pipe"]
    task          = st.session_state["automl_task"]
    target_col    = st.session_state["automl_target"]
    feature_cols  = st.session_state["automl_features"]
    class_names   = st.session_state["automl_class_names"]
    X_test        = st.session_state["automl_X_test"]
    y_test        = st.session_state["automl_y_test"]
    num_features  = st.session_state["automl_num_features"]
    sort_col      = "Accuracy" if task == "Classification" else "R² Score"

    st.markdown('<div class="section-header">Step 3 — Model Comparison</div>', unsafe_allow_html=True)

    # Top metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-pill"><div class="pill-val">🥇</div><div class="pill-lbl">Best Model</div><div style="font-weight:700;margin-top:0.3rem;font-size:0.85rem">{best_name}</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-pill"><div class="pill-val">{best_score:.1%}</div><div class="pill-lbl">{sort_col}</div></div>', unsafe_allow_html=True)
    with m3:
        n_models = len(results_df)
        st.markdown(f'<div class="metric-pill"><div class="pill-val">{n_models}</div><div class="pill-lbl">Models Trained</div></div>', unsafe_allow_html=True)
    with m4:
        cv_score = results_df.iloc[0].get("CV Score", 0)
        st.markdown(f'<div class="metric-pill"><div class="pill-val">{cv_score:.1%}</div><div class="pill-lbl">CV Score</div></div>', unsafe_allow_html=True)

    # Results table
    st.markdown("#### 📊 All Models Ranked")
    display_df = results_df.copy()
    display_df.index = display_df.index + 1
    st.dataframe(display_df, use_container_width=True,
                 column_config={sort_col: st.column_config.ProgressColumn(sort_col, min_value=0, max_value=1)})

    # Model comparison bar chart
    fig_bar = px.bar(
        results_df, x="Model", y=sort_col,
        color=sort_col, color_continuous_scale="Purples",
        title=f"Model Comparison — {sort_col}",
        text=results_df[sort_col].apply(lambda x: f"{x:.3f}")
    )
    fig_bar.update_traces(textposition="outside")
    fig_bar.update_layout(template="plotly_dark", height=380, showlegend=False,
                          xaxis_tickangle=-15)
    st.plotly_chart(fig_bar, use_container_width=True, key="model_comparison")

    # ── Step 4: Best Model Deep Dive ──────────────────────────────────────────
    st.markdown(f'<div class="section-header">Step 4 — Best Model Deep Dive: {best_name}</div>', unsafe_allow_html=True)

    y_pred = best_pipe.predict(X_test)

    if task == "Classification":
        tab_conf, tab_report, tab_fi = st.tabs(["Confusion Matrix", "Classification Report", "Feature Importance"])

        with tab_conf:
            cm = confusion_matrix(y_test, y_pred)
            labels = class_names if class_names is not None else [str(i) for i in range(len(cm))]
            labels = [str(l)[:20] for l in labels]
            fig_cm = px.imshow(
                cm, text_auto=True,
                x=labels, y=labels,
                color_continuous_scale="Purples",
                title="Confusion Matrix",
                labels=dict(x="Predicted", y="Actual")
            )
            fig_cm.update_layout(template="plotly_dark", height=420)
            st.plotly_chart(fig_cm, use_container_width=True, key="conf_matrix")
            st.caption(f"Diagonal = correct predictions. Off-diagonal = errors.")

        with tab_report:
            cn = [str(c)[:15] for c in (class_names if class_names is not None else sorted(set(y_test)))]
            report = classification_report(y_test, y_pred, target_names=cn, output_dict=True)
            report_df = pd.DataFrame(report).transpose().round(3)
            st.dataframe(report_df, use_container_width=True)

        with tab_fi:
            try:
                model_step = best_pipe.named_steps["model"]
                if hasattr(model_step, "feature_importances_"):
                    importances = model_step.feature_importances_
                elif hasattr(model_step, "coef_"):
                    importances = np.abs(model_step.coef_[0]) if model_step.coef_.ndim > 1 else np.abs(model_step.coef_)
                else:
                    raise ValueError("Model doesn't support feature importance")

                # Get transformed feature names
                prep = best_pipe.named_steps["preprocessor"]
                num_names = num_features
                try:
                    cat_enc = prep.named_transformers_["cat"].named_steps["encoder"]
                    cat_names = cat_enc.get_feature_names_out(st.session_state["automl_cat_features"]).tolist()
                except Exception:
                    cat_names = []
                all_feat_names = num_names + cat_names

                n = min(len(importances), len(all_feat_names))
                fi_df = pd.DataFrame({
                    "Feature":    all_feat_names[:n],
                    "Importance": importances[:n]
                }).sort_values("Importance", ascending=True).tail(15)

                fig_fi = px.bar(
                    fi_df, x="Importance", y="Feature",
                    orientation="h", title="Top Feature Importances",
                    color="Importance", color_continuous_scale="Purples"
                )
                fig_fi.update_layout(template="plotly_dark", height=450, showlegend=False)
                st.plotly_chart(fig_fi, use_container_width=True, key="feat_importance")

            except Exception as e:
                st.info(f"Feature importance not available for {best_name}: {e}")

    else:  # Regression
        tab_scatter, tab_resid, tab_fi = st.tabs(["Actual vs Predicted", "Residuals", "Feature Importance"])

        with tab_scatter:
            r2   = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            scatter_df = pd.DataFrame({"Actual": y_test, "Predicted": y_pred})
            fig_sc = px.scatter(
                scatter_df, x="Actual", y="Predicted",
                title=f"Actual vs Predicted (R²={r2:.4f}, RMSE={rmse:.4f})",
                opacity=0.6, trendline="ols",
                color_discrete_sequence=["#a78bfa"]
            )
            fig_sc.add_shape(type="line",
                             x0=scatter_df["Actual"].min(), y0=scatter_df["Actual"].min(),
                             x1=scatter_df["Actual"].max(), y1=scatter_df["Actual"].max(),
                             line=dict(color="white", dash="dash", width=1))
            fig_sc.update_layout(template="plotly_dark", height=420)
            st.plotly_chart(fig_sc, use_container_width=True, key="scatter_plot")

        with tab_resid:
            residuals = np.array(y_test) - np.array(y_pred)
            fig_res = px.histogram(residuals, nbins=40, title="Residual Distribution",
                                   color_discrete_sequence=["#7c3aed"])
            fig_res.update_layout(template="plotly_dark", height=360)
            st.plotly_chart(fig_res, use_container_width=True, key="residuals")

        with tab_fi:
            try:
                model_step = best_pipe.named_steps["model"]
                if hasattr(model_step, "feature_importances_"):
                    importances = model_step.feature_importances_
                elif hasattr(model_step, "coef_"):
                    importances = np.abs(model_step.coef_)
                else:
                    raise ValueError("Not supported")

                prep = best_pipe.named_steps["preprocessor"]
                num_names = num_features
                try:
                    cat_enc = prep.named_transformers_["cat"].named_steps["encoder"]
                    cat_names = cat_enc.get_feature_names_out(st.session_state["automl_cat_features"]).tolist()
                except Exception:
                    cat_names = []
                all_feat_names = num_names + cat_names
                n = min(len(importances), len(all_feat_names))
                fi_df = pd.DataFrame({
                    "Feature":    all_feat_names[:n],
                    "Importance": importances[:n]
                }).sort_values("Importance", ascending=True).tail(15)

                fig_fi2 = px.bar(fi_df, x="Importance", y="Feature",
                                 orientation="h", title="Top Feature Importances",
                                 color="Importance", color_continuous_scale="Purples")
                fig_fi2.update_layout(template="plotly_dark", height=450, showlegend=False)
                st.plotly_chart(fig_fi2, use_container_width=True, key="feat_imp_reg")
            except Exception as e:
                st.info(f"Feature importance not available: {e}")

    # ── Step 5: AI Explanation ────────────────────────────────────────────────
    st.markdown('<div class="section-header">Step 5 — AI Explanation & Business Insights</div>', unsafe_allow_html=True)

    if st.button("🧠 Generate AI Explanation", type="primary"):
        with st.spinner("🤖 Generating insights…"):
            # Build metrics string
            best_row = results_df.iloc[0].to_dict()
            metrics_str = ", ".join([f"{k}: {v}" for k, v in best_row.items() if k != "Model"])

            # Feature importance summary
            try:
                model_step = best_pipe.named_steps["model"]
                prep = best_pipe.named_steps["preprocessor"]
                num_names = num_features
                try:
                    cat_enc = prep.named_transformers_["cat"].named_steps["encoder"]
                    cat_names = cat_enc.get_feature_names_out(st.session_state["automl_cat_features"]).tolist()
                except Exception:
                    cat_names = []
                all_feat_names = num_names + cat_names

                if hasattr(model_step, "feature_importances_"):
                    imps = model_step.feature_importances_
                    n = min(len(imps), len(all_feat_names))
                    fi_pairs = sorted(zip(all_feat_names[:n], imps[:n]), key=lambda x: x[1], reverse=True)[:5]
                    fi_str = ", ".join([f"{f} ({v:.3f})" for f,v in fi_pairs])
                else:
                    fi_str = "Not available for this model"
            except Exception:
                fi_str = "Not available"

            all_model_str = results_df.to_string(index=False)

            prompt = f"""
You are an expert ML engineer and data scientist. Explain these AutoML results to a business audience.

Dataset: {upload.get('filename','dataset')} | Target: {target_col} | Task: {task}
Training rows: {df.shape[0]:,} | Features used: {len(feature_cols)}

All models trained and their performance:
{all_model_str}

Best model: {best_name}
Best model metrics: {metrics_str}
Top important features: {fi_str}

Write a comprehensive explanation covering:
1. **Model Performance Summary** — how well did the best model perform and what does it mean
2. **Why {best_name} Won** — explain why this model outperformed others
3. **Key Predictive Features** — what drives predictions and business interpretation
4. **Model Reliability** — cross-validation score interpretation, any concerns
5. **Business Recommendations** — 3 specific actionable recommendations based on findings
6. **Limitations & Next Steps** — what could improve the model

Use clear headings, be specific with numbers, and make it accessible to non-technical stakeholders.
"""
            explanation = call_llm(prompt, system="You are an expert ML engineer. Explain results clearly for business stakeholders.", max_tokens=1500)
            st.session_state["automl_explanation"] = explanation

            # Save to analyses
            save_analysis(user["id"], upload.get("id", 0),
                          f"AutoML: {task} on {target_col}. Best: {best_name} ({sort_col}: {best_score:.4f})",
                          explanation)

    if st.session_state.get("automl_explanation"):
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown(st.session_state["automl_explanation"])
        st.markdown('</div>', unsafe_allow_html=True)

        # Download explanation
        st.download_button(
            "📥 Download AutoML Report",
            data=f"AutoML Report\n{'='*50}\nDataset: {upload.get('filename','')}\nTarget: {target_col}\nTask: {task}\nBest Model: {best_name} | {sort_col}: {best_score:.4f}\n\n{st.session_state['automl_explanation']}",
            file_name=f"automl_report_{target_col}.txt",
            mime="text/plain"
        )

    # ── Step 6: Make Predictions ──────────────────────────────────────────────
    st.markdown('<div class="section-header">Step 6 — Make Predictions on New Data</div>', unsafe_allow_html=True)

    st.markdown("Enter values for each feature to get a prediction from the best model:")

    with st.form("predict_form"):
        input_data = {}
        pred_cols = st.columns(3)
        for i, col in enumerate(feature_cols):
            with pred_cols[i % 3]:
                col_data = df[col].dropna()
                if df[col].dtype in [np.float64, np.int64, float, int]:
                    val = st.number_input(
                        col,
                        value=float(col_data.median()),
                        key=f"pred_{col}"
                    )
                else:
                    unique_vals = col_data.unique().tolist()[:50]
                    val = st.selectbox(col, options=unique_vals, key=f"pred_{col}")
                input_data[col] = val

        predict_btn = st.form_submit_button("🔮 Predict", use_container_width=True)

    if predict_btn:
        try:
            input_df = pd.DataFrame([input_data])
            prediction = best_pipe.predict(input_df)[0]
            if task == "Classification" and st.session_state.get("automl_le"):
                le = st.session_state["automl_le"]
                pred_label = le.inverse_transform([int(prediction)])[0]
            else:
                pred_label = f"{prediction:.4f}"

            # Probability for classification
            prob_str = ""
            if task == "Classification" and hasattr(best_pipe, "predict_proba"):
                try:
                    probs = best_pipe.predict_proba(input_df)[0]
                    le = st.session_state.get("automl_le")
                    if le is not None:
                        prob_dict = {str(le.inverse_transform([i])[0]): round(float(p)*100, 1) for i,p in enumerate(probs)}
                    else:
                        prob_dict = {str(i): round(float(p)*100, 1) for i,p in enumerate(probs)}
                    top3 = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)[:3]
                    prob_str = " | ".join([f"{k}: {v}%" for k,v in top3])
                except Exception:
                    pass

            st.success(f"🔮 **Predicted {target_col}:** `{pred_label}`")
            if prob_str:
                st.info(f"📊 **Confidence:** {prob_str}")

            # Quick LLM interpretation
            provider = get_llm_provider()
            if provider != "fallback":
                interp = call_llm(
                    f"The ML model predicted {target_col} = '{pred_label}' for input: {input_data}. In 2 sentences, explain what this prediction means in practical/business terms.",
                    system="You are a concise data analyst. Explain ML predictions simply.",
                    max_tokens=150
                )
                st.markdown(f"**💡 Interpretation:** {interp}")

        except Exception as e:
            st.error(f"Prediction error: {e}")

    # ── Step 7: Predictive Q&A ────────────────────────────────────────────────
    st.markdown('<div class="section-header">Step 7 — Ask Questions About Your Predictions</div>', unsafe_allow_html=True)
    st.markdown("Ask anything about the model, predictions, or dataset patterns:")

    if "automl_chat" not in st.session_state:
        st.session_state["automl_chat"] = []

    # Display previous automl chat
    for msg in st.session_state["automl_chat"]:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["message"])

    automl_question = st.chat_input("e.g. Which features matter most? What drives this prediction?", key="automl_chat_input")

    if automl_question:
        st.session_state["automl_chat"].append({"role": "user", "message": automl_question})
        with st.chat_message("user"):
            st.markdown(automl_question)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing…"):
                # Build rich context
                best_row    = results_df.iloc[0].to_dict()
                metrics_str = ", ".join([f"{k}: {v}" for k,v in best_row.items() if k != "Model"])
                all_results = results_df.to_string(index=False)
                history_ctx = "\n".join([
                    f"{'User' if m['role']=='user' else 'Assistant'}: {m['message'][:200]}"
                    for m in st.session_state["automl_chat"][-6:-1]
                ])

                system = """You are an expert ML engineer and data scientist assistant.
Answer questions about the trained AutoML models, predictions, and dataset patterns.
Be specific, cite exact numbers from the results, and give actionable advice.
Use markdown formatting with bold headings and bullet points."""

                prompt = f"""AutoML Context:
- Dataset: {upload.get('filename','dataset')} | Rows: {df.shape[0]:,} | Columns: {df.shape[1]}
- Task: {task} | Target: {target_col} | Features: {len(feature_cols)}
- Best Model: {best_name} | {sort_col}: {best_score:.4f}
- All model results:\n{all_results}
- Dataset columns: {', '.join(df.columns.tolist())}

Previous conversation:
{history_ctx}

Question: {automl_question}

Answer with specific details from the AutoML results:"""

                answer = call_llm(prompt, system=system, max_tokens=1000)
                st.markdown(answer)

        st.session_state["automl_chat"].append({"role": "assistant", "message": answer})