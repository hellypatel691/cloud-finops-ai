"""
Feature engineering for the forecasting pipeline.
Builds daily spend time-series from BillingRecord objects
and creates lag / rolling features for LightGBM.
"""
from __future__ import annotations

import pandas as pd
import numpy as np


def build_daily_series(records: list, group_by: str | None = None) -> pd.DataFrame:
    """
    Aggregate BillingRecord objects into a daily spend time-series.

    Parameters
    ----------
    records  : list of BillingRecord ORM objects
    group_by : optional column to split by ('cloud_provider' | 'service' | None)

    Returns
    -------
    DataFrame with columns: ds (date), y (total cost), [group]
    """
    rows = [
        {
            "ds":             pd.to_datetime(r.date),
            "y":              float(r.total_cost or 0),
            "cloud_provider": r.cloud_provider,
            "service":        r.service,
        }
        for r in records
    ]
    if not rows:
        return pd.DataFrame(columns=["ds", "y"])

    df = pd.DataFrame(rows)

    if group_by and group_by in df.columns:
        daily = (
            df.groupby([pd.Grouper(key="ds", freq="D"), group_by])["y"]
            .sum()
            .reset_index()
            .rename(columns={group_by: "group"})
        )
    else:
        daily = (
            df.groupby(pd.Grouper(key="ds", freq="D"))["y"]
            .sum()
            .reset_index()
        )

    daily = daily.sort_values("ds").reset_index(drop=True)
    # Fill any missing days with 0
    full_range = pd.date_range(daily["ds"].min(), daily["ds"].max(), freq="D")
    if group_by:
        groups = daily["group"].unique()
        frames = []
        for g in groups:
            sub = daily[daily["group"] == g].set_index("ds").reindex(full_range, fill_value=0).reset_index()
            sub.columns = ["ds", "y"]
            sub["group"] = g
            frames.append(sub)
        daily = pd.concat(frames, ignore_index=True)
    else:
        daily = daily.set_index("ds").reindex(full_range, fill_value=0).reset_index()
        daily.columns = ["ds", "y"]

    return daily


def add_lgbm_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add time-series features needed by LightGBM.
    Operates on a single series (no group column).
    """
    df = df.copy().sort_values("ds").reset_index(drop=True)

    df["day_of_week"]  = df["ds"].dt.dayofweek
    df["day_of_month"] = df["ds"].dt.day
    df["month"]        = df["ds"].dt.month
    df["quarter"]      = df["ds"].dt.quarter
    df["is_weekend"]   = (df["day_of_week"] >= 5).astype(int)
    df["is_month_end"] = df["ds"].dt.is_month_end.astype(int)

    df["lag_1"]  = df["y"].shift(1)
    df["lag_7"]  = df["y"].shift(7)
    df["lag_14"] = df["y"].shift(14)
    df["lag_30"] = df["y"].shift(30)

    df["rolling_mean_7"]  = df["y"].shift(1).rolling(7,  min_periods=1).mean()
    df["rolling_mean_14"] = df["y"].shift(1).rolling(14, min_periods=1).mean()
    df["rolling_mean_30"] = df["y"].shift(1).rolling(30, min_periods=1).mean()
    df["rolling_std_7"]   = df["y"].shift(1).rolling(7,  min_periods=1).std().fillna(0)

    df = df.fillna(0)
    return df


LGBM_FEATURE_COLS = [
    "day_of_week", "day_of_month", "month", "quarter",
    "is_weekend", "is_month_end",
    "lag_1", "lag_7", "lag_14", "lag_30",
    "rolling_mean_7", "rolling_mean_14", "rolling_mean_30", "rolling_std_7",
]
