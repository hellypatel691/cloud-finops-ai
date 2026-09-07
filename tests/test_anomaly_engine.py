"""Tests for the anomaly detection ML pipeline."""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from datetime import date, timedelta

from app.ml.features import records_to_dataframe, engineer_features, get_feature_matrix
from app.ml.statistical import zscore_detection, iqr_detection, statistical_ensemble
from app.ml.isolation_forest import run_isolation_forest
from app.ml.anomaly_engine import run_anomaly_detection, ANOMALY_THRESHOLD


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_mock_records(n=60, spike_idx=None):
    """Create a list of mock BillingRecord-like objects."""
    records = []
    base_date = date(2023, 1, 1)
    for i in range(n):
        r = MagicMock()
        r.id             = i + 1
        r.date           = base_date + timedelta(days=i)
        r.cloud_provider = "AWS"
        r.service        = "EC2"
        r.environment    = "prod"
        r.region         = "us-east-1"
        r.total_cost     = 100.0 + np.random.normal(0, 5)
        r.usage_quantity = 10.0
        r.anomaly_score  = 0.0
        r.is_anomaly     = False
        records.append(r)

    # Inject a spike
    if spike_idx is not None and spike_idx < n:
        records[spike_idx].total_cost = 9999.0

    return records


# ── Feature engineering ───────────────────────────────────────────────────────

def test_records_to_dataframe():
    records = make_mock_records(10)
    df = records_to_dataframe(records)
    assert len(df) == 10
    assert "total_cost" in df.columns
    assert "date" in df.columns


def test_engineer_features_adds_columns():
    records = make_mock_records(30)
    df = records_to_dataframe(records)
    df = engineer_features(df)
    for col in ["rolling_mean_7", "rolling_mean_30", "lag_1", "lag_7", "is_weekend"]:
        assert col in df.columns, f"Missing column: {col}"


def test_feature_matrix_shape():
    records = make_mock_records(30)
    df = records_to_dataframe(records)
    df = engineer_features(df)
    X = get_feature_matrix(df)
    assert X.ndim == 2
    assert X.shape[0] == 30
    assert not np.isnan(X).any()


# ── Statistical detectors ─────────────────────────────────────────────────────

def test_zscore_detects_spike():
    series = pd.Series([100.0] * 49 + [9999.0])
    result = zscore_detection(series, threshold=3.0)
    assert 49 in result.indices


def test_zscore_no_anomaly_uniform():
    series = pd.Series([100.0] * 50)
    result = zscore_detection(series, threshold=3.0)
    assert len(result.indices) == 0


def test_iqr_detects_outlier():
    series = pd.Series([10.0] * 48 + [1.0, 9999.0])
    result = iqr_detection(series)
    assert 49 in result.indices


def test_statistical_ensemble_returns_scores():
    records = make_mock_records(60, spike_idx=30)
    df = records_to_dataframe(records)
    df = statistical_ensemble(df)
    assert "stat_score" in df.columns
    assert "stat_anomaly" in df.columns
    assert df["stat_score"].between(0, 1).all()


def test_statistical_ensemble_flags_spike():
    records = make_mock_records(60, spike_idx=30)
    df = records_to_dataframe(records)
    df = statistical_ensemble(df)
    assert df.loc[30, "stat_anomaly"] == True


# ── Isolation Forest ──────────────────────────────────────────────────────────

def test_isolation_forest_returns_scores():
    records = make_mock_records(60, spike_idx=30)
    df = records_to_dataframe(records)
    df = run_isolation_forest(df, contamination=0.05)
    assert "if_score" in df.columns
    assert "if_anomaly" in df.columns
    assert df["if_score"].between(0, 1).all()


def test_isolation_forest_too_few_rows():
    records = make_mock_records(5)
    df = records_to_dataframe(records)
    df = run_isolation_forest(df)
    assert "if_score" in df.columns
    assert (df["if_score"] == 0.0).all()


# ── Full engine ───────────────────────────────────────────────────────────────

def test_run_anomaly_detection_returns_all_records():
    records = make_mock_records(60)
    results = run_anomaly_detection(records)
    assert len(results) == 60


def test_run_anomaly_detection_empty():
    results = run_anomaly_detection([])
    assert results == []


def test_run_anomaly_detection_scores_in_range():
    records = make_mock_records(60)
    results = run_anomaly_detection(records)
    for r in results:
        assert 0.0 <= r.anomaly_score <= 1.0


def test_run_anomaly_detection_spike_flagged():
    records = make_mock_records(80, spike_idx=40)
    results = run_anomaly_detection(records)
    spike = results[40]
    # The spike record should have a higher score than average
    avg = sum(r.anomaly_score for r in results) / len(results)
    assert spike.anomaly_score > avg


def test_anomaly_result_has_type():
    records = make_mock_records(60, spike_idx=30)
    results = run_anomaly_detection(records)
    anomalies = [r for r in results if r.is_anomaly]
    for a in anomalies:
        assert a.anomaly_type in ("Spike", "Drift", "Seasonal", "Normal")
