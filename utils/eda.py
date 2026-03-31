"""
utils/eda.py — Exploratory Data Analysis engine for InsightBot
Generates statistics, charts, and AI-ready summaries from DataFrames
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import io


# ── Data Loading ──────────────────────────────────────────────────────────────

def load_file(file_path: str, file_type: str) -> pd.DataFrame:
    """Load CSV or Excel file into a DataFrame."""
    if file_type in ("csv",):
        return pd.read_csv(file_path)
    elif file_type in ("xlsx", "xls"):
        return pd.read_excel(file_path)
    raise ValueError(f"Unsupported file type: {file_type}")


# ── Basic EDA ─────────────────────────────────────────────────────────────────

def get_basic_stats(df: pd.DataFrame) -> dict:
    """Return a dict of basic statistics."""
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()

    stats = {
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing": df.isnull().sum().to_dict(),
        "missing_pct": (df.isnull().mean() * 100).round(2).to_dict(),
        "duplicates": int(df.duplicated().sum()),
        "numeric_cols": num_cols,
        "categorical_cols": cat_cols,
    }

    if num_cols:
        desc = df[num_cols].describe().round(4)
        stats["numeric_summary"] = desc.to_dict()

    return stats


def get_summary_text(df: pd.DataFrame) -> str:
    """Human-readable summary of the dataset for LLM context."""
    stats = get_basic_stats(df)
    rows, cols = stats["shape"]
    missing_total = sum(stats["missing"].values())

    lines = [
        f"Dataset has {rows:,} rows and {cols} columns.",
        f"Numeric columns: {', '.join(stats['numeric_cols']) or 'None'}",
        f"Categorical columns: {', '.join(stats['categorical_cols']) or 'None'}",
        f"Missing values: {missing_total} total ({(missing_total / (rows * cols) * 100):.1f}% of all cells)",
        f"Duplicate rows: {stats['duplicates']}",
    ]

    if stats.get("numeric_summary"):
        for col in list(stats["numeric_cols"])[:5]:
            s = stats["numeric_summary"].get(col, {})
            lines.append(
                f"  • {col}: mean={s.get('mean', 'N/A'):.2f}, "
                f"min={s.get('min', 'N/A'):.2f}, max={s.get('max', 'N/A'):.2f}"
            )

    # Top value counts for categoricals
    for col in stats["categorical_cols"][:3]:
        top = df[col].value_counts().head(3).to_dict()
        top_str = ", ".join([f"{k}: {v}" for k, v in top.items()])
        lines.append(f"  • {col} top values: {top_str}")

    return "\n".join(lines)


# ── Visualizations ─────────────────────────────────────────────────────────────

PALETTE = px.colors.qualitative.Set2


def fig_missing_heatmap(df: pd.DataFrame):
    missing = df.isnull().astype(int)
    if missing.sum().sum() == 0:
        return None
    fig = px.imshow(
        missing.T,
        color_continuous_scale=["#2ecc71", "#e74c3c"],
        title="Missing Values Heatmap",
        labels={"color": "Missing"},
        aspect="auto",
    )
    fig.update_layout(coloraxis_showscale=False, height=300)
    return fig


def fig_distribution(df: pd.DataFrame, col: str):
    fig = make_subplots(rows=1, cols=2, subplot_titles=["Histogram", "Box Plot"])
    fig.add_trace(go.Histogram(x=df[col], name=col, marker_color=PALETTE[0]), row=1, col=1)
    fig.add_trace(go.Box(y=df[col], name=col, marker_color=PALETTE[1]), row=1, col=2)
    fig.update_layout(title=f"Distribution of {col}", showlegend=False, height=350)
    return fig


def fig_correlation_heatmap(df: pd.DataFrame):
    num = df.select_dtypes(include=np.number)
    if num.shape[1] < 2:
        return None
    corr = num.corr().round(2)
    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="RdBu_r",
        title="Correlation Matrix",
        zmin=-1,
        zmax=1,
    )
    fig.update_layout(height=450)
    return fig


def fig_categorical_bar(df: pd.DataFrame, col: str, top_n: int = 15):
    vc = df[col].value_counts().head(top_n).reset_index()
    vc.columns = [col, "count"]
    fig = px.bar(
        vc, x=col, y="count",
        title=f"Top {top_n} Values — {col}",
        color="count",
        color_continuous_scale="Blues",
    )
    fig.update_layout(showlegend=False, height=350)
    return fig


def fig_scatter(df: pd.DataFrame, x: str, y: str, color: str = None):
    kwargs = dict(x=x, y=y, title=f"{x} vs {y}", opacity=0.6, height=400)
    if color and color in df.columns:
        kwargs["color"] = color
    return px.scatter(df, **kwargs)


def fig_time_series(df: pd.DataFrame, date_col: str, val_col: str):
    tmp = df[[date_col, val_col]].dropna()
    tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
    tmp = tmp.dropna().sort_values(date_col)
    fig = px.line(tmp, x=date_col, y=val_col, title=f"{val_col} Over Time")
    fig.update_layout(height=380)
    return fig


def auto_generate_charts(df: pd.DataFrame) -> list:
    """Auto-generate a set of charts for the dataset."""
    charts = []
    num_cols = df.select_dtypes(include=np.number).columns.tolist()
    cat_cols = df.select_dtypes(exclude=np.number).columns.tolist()

    # Missing values
    miss = fig_missing_heatmap(df)
    if miss:
        charts.append(("Missing Values", miss))

    # Distributions for first 4 numeric columns
    for col in num_cols[:4]:
        charts.append((f"Distribution — {col}", fig_distribution(df, col)))

    # Correlation
    corr = fig_correlation_heatmap(df)
    if corr:
        charts.append(("Correlation Matrix", corr))

    # Bar charts for categoricals
    for col in cat_cols[:3]:
        charts.append((f"Value Counts — {col}", fig_categorical_bar(df, col)))

    # Scatter if ≥ 2 numeric columns
    if len(num_cols) >= 2:
        charts.append((f"Scatter — {num_cols[0]} vs {num_cols[1]}",
                       fig_scatter(df, num_cols[0], num_cols[1])))

    return charts
