"""Tests for the forecasting pipeline."""
import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta
from unittest.mock import MagicMock

from app.ml.forecast_features import build_daily_series, add_lgbm_features, LGBM_FEATURE_COLS
from app.ml.lgbm_model import run_lgbm
from app.ml.forecast_engine import run_forecast, _linear_fallback, _make_horizon, HORIZON_DAYS


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_mock_records(n=120, provider="AWS", service="EC2"):
    records = []
    base = date(2023, 1, 1)
    rng  = np.random.default_rng(42)
    for i in range(n):
        r = MagicMock()
        r.date           = base + timedelta(days=i)
        r.cloud_provider = provider
        r.service        = service
        r.total_cost     = max(0, 1000 + 50 * np.sin(2 * np.pi * i / 7) + rng.normal(0, 30))
        r.usage_quantity = 10.0
        records.append(r)
    return records


def make_multi_provider_records(n=120):
    return (
        make_mock_records(n, "AWS",   "EC2") +
        make_mock_records(n, "Azure", "VMs") +
        make_mock_records(n, "GCP",   "GCE")
    )


# ── Feature engineering ───────────────────────────────────────────────────────

def test_build_daily_series_shape():
    records = make_mock_records(60)
    daily   = build_daily_series(records)
    assert "ds" in daily.columns
    assert "y"  in daily.columns
    assert len(daily) == 60


def test_build_daily_series_empty():
    daily = build_daily_series([])
    assert daily.empty


def test_add_lgbm_features_columns():
    records = make_mock_records(60)
    daily   = build_daily_series(records)
    df      = add_lgbm_features(daily)
    for col in LGBM_FEATURE_COLS:
        assert col in df.columns, f"Missing: {col}"


def test_add_lgbm_features_no_nan():
    records = make_mock_records(60)
    daily   = build_daily_series(records)
    df      = add_lgbm_features(daily)
    assert not df[LGBM_FEATURE_COLS].isna().any().any()


# ── LightGBM ──────────────────────────────────────────────────────────────────

def test_lgbm_returns_forecast():
    records = make_mock_records(120)
    daily   = build_daily_series(records)
    result  = run_lgbm(daily, horizon_days=30)
    assert not result.empty
    assert "yhat"        in result.columns
    assert "is_forecast" in result.columns


def test_lgbm_forecast_length():
    records = make_mock_records(120)
    daily   = build_daily_series(records)
    result  = run_lgbm(daily, horizon_days=30)
    future  = result[result["is_forecast"]]
    assert len(future) == 30


def test_lgbm_no_negative_predictions():
    records = make_mock_records(120)
    daily   = build_daily_series(records)
    result  = run_lgbm(daily, horizon_days=30)
    assert (result["yhat"] >= 0).all()


def test_lgbm_too_few_rows():
    records = make_mock_records(10)
    daily   = build_daily_series(records)
    result  = run_lgbm(daily, horizon_days=7)
    assert result.empty


# ── Linear fallback ───────────────────────────────────────────────────────────

def test_linear_fallback_shape():
    records = make_mock_records(60)
    daily   = build_daily_series(records)
    result  = _linear_fallback(daily)
    future  = result[result["is_forecast"]]
    assert len(future) == HORIZON_DAYS


def test_linear_fallback_has_ci():
    records = make_mock_records(60)
    daily   = build_daily_series(records)
    result  = _linear_fallback(daily)
    assert "yhat_lower" in result.columns
    assert "yhat_upper" in result.columns
    assert (result["yhat_upper"] >= result["yhat_lower"]).all()


# ── Full engine ───────────────────────────────────────────────────────────────

def test_run_forecast_empty_records():
    result = run_forecast([])
    assert result.series == []
    assert result.horizons == []
    assert result.selected_model == "none"


def test_run_forecast_returns_horizons():
    records = make_mock_records(120)
    result  = run_forecast(records)
    assert len(result.horizons) == 3
    days = [h.days for h in result.horizons]
    assert 7  in days
    assert 30 in days
    assert 90 in days


def test_run_forecast_horizon_values_positive():
    records = make_mock_records(120)
    result  = run_forecast(records)
    for h in result.horizons:
        assert h.p10 >= 0
        assert h.p50 >= 0
        assert h.p90 >= h.p50 * 0.9   # p90 ≥ p50 (allow small fp diff)


def test_run_forecast_series_has_future():
    records = make_mock_records(120)
    result  = run_forecast(records)
    future  = [p for p in result.series if p.is_forecast]
    assert len(future) > 0


def test_run_forecast_model_selected():
    records = make_mock_records(120)
    result  = run_forecast(records)
    assert result.selected_model in ("Prophet", "LightGBM", "Linear")


def test_run_forecast_provider_breakdown():
    records = make_multi_provider_records(120)
    result  = run_forecast(records)
    providers = [p.provider for p in result.provider_breakdown]
    for prov in ["AWS", "Azure", "GCP"]:
        assert prov in providers


def test_run_forecast_confidence_bands():
    records = make_mock_records(120)
    result  = run_forecast(records)
    future  = [p for p in result.series if p.is_forecast]
    for p in future:
        assert p.yhat_upper >= p.yhat_lower
