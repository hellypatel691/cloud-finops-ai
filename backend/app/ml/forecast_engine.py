"""
Forecast Engine — orchestrates Prophet + LightGBM,
selects the best model by MAE, and returns unified results.

Output structure:
  - daily series: historical actuals + forecast with confidence bands
  - horizon summaries: 7d / 30d / 90d totals (P10 / P50 / P90)
  - per-provider breakdown
  - model comparison metrics
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import pandas as pd

from app.ml.forecast_features import build_daily_series
from app.ml.prophet_model import run_prophet
from app.ml.lgbm_model import run_lgbm
from app.utils.logger import get_logger

logger = get_logger(__name__)

HORIZON_DAYS = 90          # always forecast 90 days; slice for 7/30 summaries
MIN_DAYS_PROPHET = 14
MIN_DAYS_LGBM    = 30
UNCERTAINTY_BAND = 0.15    # ±15% for LightGBM (no native CI)


# ── Result types ─────────────────────────────────────────────────────────────

@dataclass
class DailyForecastPoint:
    ds:           str
    actual:       Optional[float]   # None for future dates
    yhat:         float
    yhat_lower:   float
    yhat_upper:   float
    is_forecast:  bool


@dataclass
class HorizonSummary:
    days:     int
    p10:      float
    p50:      float
    p90:      float
    total:    float


@dataclass
class ModelMetrics:
    name: str
    mae:  Optional[float]
    mape: Optional[float]
    selected: bool


@dataclass
class ProviderForecast:
    provider: str
    p10_30d:  float
    p50_30d:  float
    p90_30d:  float


@dataclass
class ForecastResult:
    series:          list[DailyForecastPoint]
    horizons:        list[HorizonSummary]        # 7d, 30d, 90d
    models:          list[ModelMetrics]
    selected_model:  str
    provider_breakdown: list[ProviderForecast]
    total_historical_spend: float
    forecast_start:  str


# ── Helpers ───────────────────────────────────────────────────────────────────

def _mape(actual: np.ndarray, predicted: np.ndarray) -> float:
    mask = actual > 1
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100)


def _make_horizon(forecast_df: pd.DataFrame, days: int) -> HorizonSummary:
    future = forecast_df[forecast_df["is_forecast"]].head(days)
    if future.empty:
        return HorizonSummary(days=days, p10=0, p50=0, p90=0, total=0)

    p50 = float(future["yhat"].sum())
    lo  = future["yhat_lower"].sum() if "yhat_lower" in future else p50 * (1 - UNCERTAINTY_BAND)
    hi  = future["yhat_upper"].sum() if "yhat_upper" in future else p50 * (1 + UNCERTAINTY_BAND)

    return HorizonSummary(
        days  = days,
        p10   = round(float(lo), 2),
        p50   = round(p50, 2),
        p90   = round(float(hi), 2),
        total = round(p50, 2),
    )


def _enrich_lgbm_with_ci(df: pd.DataFrame) -> pd.DataFrame:
    """Add yhat_lower / yhat_upper bands to LightGBM output."""
    df = df.copy()
    df["yhat_lower"] = (df["yhat"] * (1 - UNCERTAINTY_BAND)).clip(lower=0)
    df["yhat_upper"] = df["yhat"] * (1 + UNCERTAINTY_BAND)
    return df


# ── Main entry point ──────────────────────────────────────────────────────────

def run_forecast(records: list) -> ForecastResult:
    """
    Full forecasting pipeline.
    1. Build daily series from billing records
    2. Fit Prophet + LightGBM
    3. Select best model by MAE on last-30-day hold-out
    4. Return unified result
    """
    logger.info("Starting forecast pipeline on %d records", len(records))

    daily = build_daily_series(records)

    if daily.empty:
        logger.warning("No billing data — returning empty forecast")
        return ForecastResult(
            series=[], horizons=[], models=[], selected_model="none",
            provider_breakdown=[], total_historical_spend=0.0,
            forecast_start="",
        )

    total_hist = float(daily["y"].sum())
    n_days     = len(daily)

    # ── Validation split for model comparison ─────────────────────────────────
    val_size = min(30, max(7, n_days // 6))
    train_df = daily.iloc[:-val_size]
    val_df   = daily.iloc[-val_size:]

    # ── Prophet ───────────────────────────────────────────────────────────────
    prophet_result, prophet_mae, prophet_mape = None, None, None
    if n_days >= MIN_DAYS_PROPHET:
        try:
            p_fc = run_prophet(train_df, horizon_days=val_size + HORIZON_DAYS)
            # Evaluate on val
            p_val = p_fc[p_fc["is_forecast"]].head(val_size)
            if len(p_val) == val_size:
                prophet_mae  = float(np.mean(np.abs(val_df["y"].values - p_val["yhat"].values)))
                prophet_mape = _mape(val_df["y"].values, p_val["yhat"].values)
            # Refit on full data
            prophet_result = run_prophet(daily, horizon_days=HORIZON_DAYS)
        except Exception as e:
            logger.error("Prophet failed: %s", e)

    # ── LightGBM ──────────────────────────────────────────────────────────────
    lgbm_result, lgbm_mae, lgbm_mape = None, None, None
    if n_days >= MIN_DAYS_LGBM:
        try:
            l_fc = run_lgbm(train_df, horizon_days=val_size + HORIZON_DAYS)
            l_val = l_fc[l_fc["is_forecast"]].head(val_size)
            if len(l_val) == val_size:
                lgbm_mae  = float(np.mean(np.abs(val_df["y"].values - l_val["yhat"].values)))
                lgbm_mape = _mape(val_df["y"].values, l_val["yhat"].values)
            lgbm_result = _enrich_lgbm_with_ci(run_lgbm(daily, horizon_days=HORIZON_DAYS))
        except Exception as e:
            logger.error("LightGBM failed: %s", e)

    # ── Model selection ───────────────────────────────────────────────────────
    candidates = {}
    if prophet_result is not None and prophet_mae is not None:
        candidates["Prophet"]  = (prophet_mae,  prophet_result)
    if lgbm_result   is not None and lgbm_mae   is not None:
        candidates["LightGBM"] = (lgbm_mae,     lgbm_result)

    if candidates:
        selected_name = min(candidates, key=lambda k: candidates[k][0])
        selected_df   = candidates[selected_name][1]
        logger.info("Selected model: %s (MAE=%.2f)", selected_name, candidates[selected_name][0])
    elif prophet_result is not None:
        selected_name, selected_df = "Prophet", prophet_result
    elif lgbm_result is not None:
        selected_name, selected_df = "LightGBM", lgbm_result
    else:
        # Fallback: linear trend
        logger.warning("Both models failed — using linear trend fallback")
        selected_name = "Linear"
        selected_df   = _linear_fallback(daily)

    # ── Build daily series ────────────────────────────────────────────────────
    actuals = dict(zip(daily["ds"].dt.strftime("%Y-%m-%d"), daily["y"]))
    series: list[DailyForecastPoint] = []

    for _, row in selected_df.iterrows():
        ds_str = row["ds"].strftime("%Y-%m-%d") if hasattr(row["ds"], "strftime") else str(row["ds"])[:10]
        series.append(DailyForecastPoint(
            ds          = ds_str,
            actual      = round(actuals[ds_str], 2) if ds_str in actuals else None,
            yhat        = round(float(row["yhat"]), 2),
            yhat_lower  = round(float(row.get("yhat_lower", row["yhat"] * 0.85)), 2),
            yhat_upper  = round(float(row.get("yhat_upper", row["yhat"] * 1.15)), 2),
            is_forecast = bool(row["is_forecast"]),
        ))

    # ── Horizon summaries ─────────────────────────────────────────────────────
    horizons = [_make_horizon(selected_df, d) for d in [7, 30, 90]]

    # ── Model metrics ─────────────────────────────────────────────────────────
    models = [
        ModelMetrics("Prophet",  prophet_mae,  prophet_mape,  selected_name == "Prophet"),
        ModelMetrics("LightGBM", lgbm_mae,     lgbm_mape,     selected_name == "LightGBM"),
    ]

    # ── Provider breakdown ────────────────────────────────────────────────────
    provider_breakdown = _provider_forecast(records, HORIZON_DAYS)

    forecast_start = selected_df[selected_df["is_forecast"]]["ds"].min()
    forecast_start = forecast_start.strftime("%Y-%m-%d") if pd.notna(forecast_start) else ""

    return ForecastResult(
        series                = series,
        horizons              = horizons,
        models                = models,
        selected_model        = selected_name,
        provider_breakdown    = provider_breakdown,
        total_historical_spend = round(total_hist, 2),
        forecast_start        = forecast_start,
    )


def _linear_fallback(daily: pd.DataFrame) -> pd.DataFrame:
    """Simple linear extrapolation when ML models are unavailable."""
    n  = len(daily)
    xs = np.arange(n)
    ys = daily["y"].values
    slope, intercept = np.polyfit(xs, ys, 1)

    last_date = daily["ds"].max()
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, HORIZON_DAYS + 1)]
    future_yhats = [max(0, slope * (n + i) + intercept) for i in range(HORIZON_DAYS)]

    hist = daily[["ds", "y"]].rename(columns={"y": "yhat"}).copy()
    hist["yhat_lower"] = hist["yhat"] * 0.85
    hist["yhat_upper"] = hist["yhat"] * 1.15
    hist["is_forecast"] = False

    future = pd.DataFrame({
        "ds":          future_dates,
        "yhat":        future_yhats,
        "yhat_lower": [v * 0.85 for v in future_yhats],
        "yhat_upper": [v * 1.15 for v in future_yhats],
        "is_forecast": True,
    })

    return pd.concat([hist, future], ignore_index=True)


def _provider_forecast(records: list, horizon: int) -> list[ProviderForecast]:
    """Generate 30-day P10/P50/P90 forecast per cloud provider."""
    providers = list({r.cloud_provider for r in records})
    result    = []

    for p in sorted(providers):
        p_records = [r for r in records if r.cloud_provider == p]
        daily     = build_daily_series(p_records)
        if daily.empty or len(daily) < 7:
            continue

        # Use last 30 days average as P50 baseline
        last_30 = daily.tail(30)["y"].mean()
        p50 = round(last_30 * 30, 2)
        result.append(ProviderForecast(
            provider = p,
            p10_30d  = round(p50 * 0.85, 2),
            p50_30d  = p50,
            p90_30d  = round(p50 * 1.18, 2),
        ))

    return result
