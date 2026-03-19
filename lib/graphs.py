import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path


PALETTE = [
    "#4C72B0", "#DD8452", "#55A868", "#C44E52",
    "#8172B3", "#937860", "#DA8BC3", "#8C8C8C",
    "#CCB974", "#64B5CD",
]

CHART_STYLE = {
    "figure.facecolor":  "#ffffff",
    "axes.facecolor":    "#f9f9f9",
    "axes.edgecolor":    "#cccccc",
    "axes.grid":         True,
    "grid.color":        "#e0e0e0",
    "grid.linestyle":    "--",
    "grid.linewidth":    0.7,
    "font.family":       "DejaVu Sans",
    "font.size":         11,
    "axes.titlesize":    14,
    "axes.titleweight":  "bold",
    "axes.labelsize":    11,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
}

_MIN_NUMERIC = {
    "barchart":    1,
    "linechart":   1,
    "piechart":    1,
    "histogram":   1,
    "scatterplot": 2,
    "areachart":   1,
    "bubblechart": 3,
}

_TYPE_ALIASES = {
    "bar":          "barchart",
    "bar_chart":    "barchart",
    "barchart":     "barchart",
    "line":         "linechart",
    "line_chart":   "linechart",
    "linechart":    "linechart",
    "pie":          "piechart",
    "pie_chart":    "piechart",
    "piechart":     "piechart",
    "hist":         "histogram",
    "histogram":    "histogram",
    "scatter":      "scatterplot",
    "scatter_plot": "scatterplot",
    "scatterplot":  "scatterplot",
    "area":         "areachart",
    "area_chart":   "areachart",
    "areachart":    "areachart",
    "bubble":       "bubblechart",
    "bubble_chart": "bubblechart",
    "bubblechart":  "bubblechart",
}

OUTPUT_PATH = "static/chart.png"



def _apply_style():
    plt.rcParams.update(CHART_STYLE)


def _to_num(series):
    return pd.to_numeric(series, errors="coerce")


def _classify(df, columns, text_hint):
    """Split columns into (numeric_cols, text_cols)."""
    text_hint_set = set(text_hint or [])
    numeric_cols, text_cols = [], []
    for col in columns:
        if col not in df.columns:
            continue
        if col in text_hint_set:
            text_cols.append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            numeric_cols.append(col)
        else:
            text_cols.append(col)
    return numeric_cols, text_cols


def _save(fig, path):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def _normalise_type(raw):
    key = raw.lower().replace(" ", "").replace("_", "").replace("-", "")
    return _TYPE_ALIASES.get(key, key)



def _barchart(df, num_cols, txt_cols):
    categories = df[txt_cols[0]].astype(str) if txt_cols else df.index.astype(str)
    x = np.arange(len(categories))
    bar_w = 0.8 / max(len(num_cols), 1)

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, col in enumerate(num_cols):
        ax.bar(x + i * bar_w, _to_num(df[col]), width=bar_w,
               label=col, color=PALETTE[i % len(PALETTE)], edgecolor="white")

    ax.set_xticks(x + bar_w * (len(num_cols) - 1) / 2)
    ax.set_xticklabels(categories, rotation=30, ha="right")
    ax.set_xlabel(txt_cols[0] if txt_cols else "Index")
    ax.set_ylabel("Value")
    ax.set_title("Bar Chart")
    if len(num_cols) > 1:
        ax.legend()
    return fig


def _linechart(df, num_cols, txt_cols):
    x_vals = df[txt_cols[0]].astype(str) if txt_cols else df.index.astype(str)
    x_idx = np.arange(len(x_vals))

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, col in enumerate(num_cols):
        ax.plot(x_idx, _to_num(df[col]), marker="o", markersize=4,
                label=col, color=PALETTE[i % len(PALETTE)], linewidth=2)

    ax.set_xticks(x_idx)
    ax.set_xticklabels(x_vals, rotation=30, ha="right")
    ax.set_xlabel(txt_cols[0] if txt_cols else "Index")
    ax.set_ylabel("Value")
    ax.set_title("Line Chart")
    if len(num_cols) > 1:
        ax.legend()
    return fig


def _piechart(df, num_cols, txt_cols):
    values = _to_num(df[num_cols[0]]).fillna(0)
    labels = df[txt_cols[0]].astype(str) if txt_cols else df.index.astype(str)

    mask = values > 0
    values, labels = values[mask], labels[mask]

    fig, ax = plt.subplots(figsize=(8, 8))
    _, _, autotexts = ax.pie(
        values, labels=labels, autopct="%1.1f%%",
        colors=PALETTE[:len(values)], startangle=140,
        pctdistance=0.82,
        wedgeprops=dict(edgecolor="white", linewidth=1.5),
    )
    for at in autotexts:
        at.set_fontsize(9)
    ax.set_title(f"Pie Chart — {num_cols[0]}")
    return fig


def _histogram(df, num_cols, txt_cols):
    fig, axes = plt.subplots(1, len(num_cols), figsize=(6 * len(num_cols), 5), squeeze=False)
    for i, col in enumerate(num_cols):
        vals = _to_num(df[col]).dropna()
        bins = min(30, max(5, len(vals) // 5))
        ax = axes[0][i]
        ax.hist(vals, bins=bins, color=PALETTE[i % len(PALETTE)], edgecolor="white", alpha=0.85)
        ax.set_xlabel(col)
        ax.set_ylabel("Frequency")
        ax.set_title(f"Histogram — {col}")
    return fig


def _scatterplot(df, num_cols, txt_cols):
    x = _to_num(df[num_cols[0]])
    y = _to_num(df[num_cols[1]])

    fig, ax = plt.subplots(figsize=(8, 6))
    if txt_cols:
        groups = df[txt_cols[0]].astype(str)
        for j, grp in enumerate(groups.unique()):
            mask = groups == grp
            ax.scatter(x[mask], y[mask], label=grp,
                       color=PALETTE[j % len(PALETTE)], alpha=0.75, edgecolors="white", s=60)
        ax.legend(title=txt_cols[0], fontsize=8)
    else:
        ax.scatter(x, y, color=PALETTE[0], alpha=0.75, edgecolors="white", s=60)

    ax.set_xlabel(num_cols[0])
    ax.set_ylabel(num_cols[1])
    ax.set_title("Scatter Plot")
    return fig


def _areachart(df, num_cols, txt_cols):
    x_vals = df[txt_cols[0]].astype(str) if txt_cols else df.index.astype(str)
    x_idx = np.arange(len(x_vals))

    fig, ax = plt.subplots(figsize=(10, 5))
    if len(num_cols) == 1:
        vals = _to_num(df[num_cols[0]]).fillna(0)
        ax.fill_between(x_idx, vals, alpha=0.45, color=PALETTE[0])
        ax.plot(x_idx, vals, color=PALETTE[0], linewidth=2, label=num_cols[0])
    else:
        baseline = np.zeros(len(x_idx))
        for i, col in enumerate(num_cols):
            vals = _to_num(df[col]).fillna(0).values
            ax.fill_between(x_idx, baseline, baseline + vals,
                            alpha=0.6, color=PALETTE[i % len(PALETTE)], label=col)
            baseline += vals

    ax.set_xticks(x_idx)
    ax.set_xticklabels(x_vals, rotation=30, ha="right")
    ax.set_xlabel(txt_cols[0] if txt_cols else "Index")
    ax.set_ylabel("Value")
    ax.set_title("Area Chart")
    ax.legend()
    return fig


def _bubblechart(df, num_cols, txt_cols):
    x = _to_num(df[num_cols[0]])
    y = _to_num(df[num_cols[1]])
    sz_raw = _to_num(df[num_cols[2]]).fillna(0)

    sz_min, sz_max = sz_raw.min(), sz_raw.max()
    if sz_max > sz_min:
        sizes = 50 + 1000 * (sz_raw - sz_min) / (sz_max - sz_min)
    else:
        sizes = np.full(len(sz_raw), 200)

    fig, ax = plt.subplots(figsize=(9, 7))
    if txt_cols:
        labels = df[txt_cols[0]].astype(str)
        for j, lbl in enumerate(labels.unique()):
            mask = labels == lbl
            ax.scatter(x[mask], y[mask], s=sizes[mask], label=lbl,
                       color=PALETTE[j % len(PALETTE)], alpha=0.65,
                       edgecolors="white", linewidths=0.8)
        ax.legend(title=txt_cols[0], fontsize=8)
    else:
        ax.scatter(x, y, s=sizes, color=PALETTE[0], alpha=0.65,
                   edgecolors="white", linewidths=0.8)

    ax.set_xlabel(num_cols[0])
    ax.set_ylabel(num_cols[1])
    ax.set_title(f"Bubble Chart  (size = {num_cols[2]})")
    return fig


_BUILDERS = {
    "barchart":    _barchart,
    "linechart":   _linechart,
    "piechart":    _piechart,
    "histogram":   _histogram,
    "scatterplot": _scatterplot,
    "areachart":   _areachart,
    "bubblechart": _bubblechart,
}



def validate_chart_config(file_path: str, chart_config: dict) -> bool:
    """Check if a chart config can be plotted against the given file."""
    try:
        if not chart_config:
            return False

        df = pd.read_excel(file_path)

        raw_type = chart_config.get("type", "")
        columns = chart_config.get("columns_used") or []
        text_hint = chart_config.get("columns_used_with_text") or []

        chart_type = _normalise_type(raw_type)
        if chart_type not in _BUILDERS:
            return False

        available = [c for c in columns if c in df.columns]
        if not available:
            return False

        df_sub = df[available].copy()
        num_cols, txt_cols = _classify(df_sub, available, text_hint)

        min_num = _MIN_NUMERIC.get(chart_type, 1)
        if len(num_cols) < min_num:
            return False

        return True
    except Exception:
        return False


def generate_chart(file_path: str, chart_config: dict, colors: list = None) -> str:

    if not chart_config:
        raise ValueError("chart_config is empty")

    if colors:
        global PALETTE
        PALETTE = colors + PALETTE[len(colors):]

    df = pd.read_excel(file_path)
    df.columns = [str(c) for c in df.columns] 

    raw_type  = chart_config.get("type", "")
    columns   = chart_config.get("columns_used") or []
    text_hint = chart_config.get("columns_used_with_text") or []

    chart_type = _normalise_type(raw_type)

    if chart_type not in _BUILDERS:
        raise ValueError(f"Unknown chart type '{raw_type}'")

    available = [c for c in columns if c in df.columns]
    if not available:
        raise ValueError(
            f"None of {columns} found in file. "
            f"Available columns: {list(df.columns)}"
        )

    df_sub = df[available].copy()
    num_cols, txt_cols = _classify(df_sub, available, text_hint)

    min_num = _MIN_NUMERIC[chart_type]
    if len(num_cols) < min_num:
        raise ValueError(
            f"'{chart_type}' needs >= {min_num} numeric column(s), "
            f"found {len(num_cols)} ({num_cols}). Text cols: {txt_cols}."
        )

    _apply_style()
    fig = _BUILDERS[chart_type](df_sub, num_cols, txt_cols)
    result = _save(fig, OUTPUT_PATH)

    if colors:
        PALETTE = [
            "#4C72B0", "#DD8452", "#55A868", "#C44E52",
            "#8172B3", "#937860", "#DA8BC3", "#8C8C8C",
            "#CCB974", "#64B5CD",
        ]
    return result

