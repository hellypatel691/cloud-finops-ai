"""
Statistical anomaly detection methods:
  - Z-score
  - IQR (robust)
  - Seasonal decomposition residual Z-score
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from dataclasses import dataclass, field


@dataclass
class StatResult:
    indices: list[int]          # row indices flagged as anomalies
    scores:  list[float]        # per-row anomaly score [0, 1]
    method:  str = ""


# ── Z-score ───────────────────────────────────────────────────────────────────

def zscore_detection(series: pd.Series, threshold: float = 3.0) -> StatResult:
    """Flag values more than `threshold` standard deviations from the mean."""
    mean = series.mean()
    std  = series.std()
    if std == 0:
        return StatResult([], [0.0] * len(series), method="zscore")

    z = np.abs((series - mean) / std)
    # Normalise scores to [0, 1] using sigmoid-like squash
    scores  = (z / (z.max() + 1e-9)).tolist()
    flagged = series.index[z > threshold].tolist()
    return StatResult(flagged, scores, method="zscore")


# ── IQR ───────────────────────────────────────────────────────────────────────

def iqr_detection(series: pd.Series, factor: float = 1.5) -> StatResult:
    """Flag values outside Q1 - factor*IQR or Q3 + factor*IQR."""
    q1, q3  = series.quantile(0.25), series.quantile(0.75)
    iqr     = q3 - q1
    lo, hi  = q1 - factor * iqr, q3 + factor * iqr

    distance = np.maximum(series - hi, lo - series).clip(lower=0)
    max_d    = distance.max() + 1e-9
    scores   = (distance / max_d).tolist()
    flagged  = series.index[(series < lo) | (series > hi)].tolist()
    return StatResult(flagged, scores, method="iqr")


# ── Seasonal decomposition residual ──────────────────────────────────────────

def seasonal_decomp_detection(
    df: pd.DataFrame,
    cost_col: str = "total_cost",
    threshold: float = 3.0,
    period: int = 7,
) -> StatResult:
    """
    Aggregate to daily totals, decompose with a rolling trend, compute
    residuals and flag by Z-score.
    """
    daily = (
        df.groupby("date")[cost_col]
        .sum()
        .sort_index()
        .reset_index()
        .rename(columns={cost_col: "cost"})
    )

    if len(daily) < period * 2:
        # Not enough data — fall back to plain Z-score
        return zscore_detection(df[cost_col], threshold)

    daily["trend"]    = daily["cost"].rolling(period, center=True, min_periods=1).mean()
    daily["residual"] = daily["cost"] - daily["trend"]

    res_std  = daily["residual"].std()
    if res_std == 0:
        return StatResult([], [0.0] * len(df), method="seasonal")

    daily["z"] = np.abs(daily["residual"] / res_std)

    # Map daily flags back to individual records
    flagged_dates = set(daily.loc[daily["z"] > threshold, "date"])

    date_to_z = dict(zip(daily["date"], daily["z"]))
    max_z     = daily["z"].max() + 1e-9
    scores    = [(date_to_z.get(d, 0) / max_z) for d in df["date"]]
    flagged   = [i for i, d in enumerate(df["date"]) if d in flagged_dates]

    return StatResult(flagged, scores, method="seasonal")


# ── Ensemble ─────────────────────────────────────────────────────────────────

def statistical_ensemble(
    df: pd.DataFrame,
    cost_col: str = "total_cost",
    zscore_thresh: float = 3.0,
    iqr_factor:    float = 1.5,
    seasonal_thresh: float = 2.5,
) -> pd.DataFrame:
    """
    Run all three methods and combine scores.
    Returns df with columns: stat_score, stat_anomaly
    """
    if df.empty:
        return df

    series = df[cost_col].reset_index(drop=True)
    df     = df.reset_index(drop=True)

    r_z   = zscore_detection(series, zscore_thresh)
    r_iqr = iqr_detection(series, iqr_factor)
    r_s   = seasonal_decomp_detection(df, cost_col, seasonal_thresh)

    z_scores   = np.array(r_z.scores)
    iqr_scores = np.array(r_iqr.scores)
    s_scores   = np.array(r_s.scores[:len(df)])

    # Weighted average: seasonal carries most weight
    combined = (0.3 * z_scores + 0.3 * iqr_scores + 0.4 * s_scores)
    combined = np.clip(combined, 0, 1)

    df["stat_score"]   = combined
    df["stat_anomaly"] = combined > 0.5

    return df
