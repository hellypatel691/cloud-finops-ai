"""
Feature engineering for anomaly detection.

Takes a list of BillingRecord ORM objects and returns a
pandas DataFrame ready for model training / inference.
"""
from __future__ import annotations

import pandas as pd
import numpy as np


# Columns used as ML features
FEATURE_COLS = [
    "total_cost",
    "usage_quantity",
    "day_of_week",
    "month",
    "is_weekend",
    "rolling_mean_7",
    "rolling_std_7",
    "rolling_mean_30",
    "cost_vs_rolling_mean_7",
    "cost_vs_rolling_mean_30",
    "lag_1",
    "lag_7",
]


def records_to_dataframe(records: list) -> pd.DataFrame:
    """Convert SQLAlchemy BillingRecord objects → raw DataFrame."""
    rows = [
        {
            "id":             r.id,
            "date":           pd.to_datetime(r.date),
            "cloud_provider": r.cloud_provider,
            "service":        r.service,
            "environment":    r.environment or "unknown",
            "region":         r.region or "unknown",
            "total_cost":     float(r.total_cost or 0),
            "usage_quantity": float(r.usage_quantity or 0),
            "anomaly_score":  float(r.anomaly_score or 0),
            "is_anomaly":     bool(r.is_anomaly),
        }
        for r in records
    ]
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add time-series and statistical features."""
    if df.empty:
        return df

    df = df.copy()
    df["day_of_week"] = df["date"].dt.dayofweek
    df["month"]       = df["date"].dt.month
    df["is_weekend"]  = (df["day_of_week"] >= 5).astype(int)

    # Daily total cost series (all providers/services combined per date)
    daily = df.groupby("date")["total_cost"].transform("sum")

    df["rolling_mean_7"]  = daily.rolling(7,  min_periods=1).mean()
    df["rolling_std_7"]   = daily.rolling(7,  min_periods=1).std().fillna(0)
    df["rolling_mean_30"] = daily.rolling(30, min_periods=1).mean()

    df["cost_vs_rolling_mean_7"]  = df["total_cost"] / (df["rolling_mean_7"]  + 1e-9)
    df["cost_vs_rolling_mean_30"] = df["total_cost"] / (df["rolling_mean_30"] + 1e-9)

    df["lag_1"] = daily.shift(1).fillna(0)
    df["lag_7"] = daily.shift(7).fillna(0)

    return df


def get_feature_matrix(df: pd.DataFrame) -> np.ndarray:
    """Return the numeric feature matrix, filling any NaNs."""
    available = [c for c in FEATURE_COLS if c in df.columns]
    X = df[available].fillna(0).values.astype(np.float64)
    return X
