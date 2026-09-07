"""Tests for SHAP explainability and root cause attribution."""
import pytest
import numpy as np
from datetime import date, timedelta
from unittest.mock import MagicMock

from app.ml.shap_explainer import run_shap, _human_reason
from app.ml.root_cause import run_root_cause, _breakdown, RootCauseResult
from app.ml.features import records_to_dataframe


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_records(n=80, provider="AWS", service="EC2", environment="prod", region="us-east-1"):
    rng  = np.random.default_rng(0)
    base = date(2023, 1, 1)
    recs = []
    for i in range(n):
        r = MagicMock()
        r.id             = i + 1
        r.date           = base + timedelta(days=i)
        r.cloud_provider = provider
        r.service        = service
        r.environment    = environment
        r.region         = region
        r.department     = "Engineering"
        r.total_cost     = max(0, 500 + rng.normal(0, 40))
        r.usage_quantity = 10.0
        r.anomaly_score  = 0.0
        r.is_anomaly     = False
        recs.append(r)
    # inject spikes at safe indices
    if n > 20:
        recs[10].total_cost = 9000.0
    if n > 40:
        recs[30].total_cost = 7500.0
    return recs


def make_multi_records(n=80):
    return (
        make_records(n, "AWS",   "EC2",      "prod",    "us-east-1") +
        make_records(n, "Azure", "VMs",      "staging", "eu-west-1") +
        make_records(n, "GCP",   "BigQuery", "dev",     "us-central1")
    )


# ── SHAP ─────────────────────────────────────────────────────────────────────

def test_shap_returns_global_importance():
    records = make_records(80)
    result  = run_shap(records)
    assert len(result.global_importance) > 0


def test_shap_importance_sums_to_100():
    records = make_records(80)
    result  = run_shap(records)
    total   = sum(f.importance for f in result.global_importance)
    assert abs(total - 100.0) < 1.0   # allow small float diff


def test_shap_importance_sorted_descending():
    records = make_records(80)
    result  = run_shap(records)
    imps    = [f.importance for f in result.global_importance]
    assert imps == sorted(imps, reverse=True)


def test_shap_direction_values():
    records = make_records(80)
    result  = run_shap(records)
    valid   = {"increases_risk", "decreases_risk", "neutral"}
    for f in result.global_importance:
        assert f.direction in valid


def test_shap_record_explanations_returned():
    records = make_records(80)
    result  = run_shap(records, top_n_records=5)
    assert len(result.record_explanations) <= 5


def test_shap_record_has_contributions():
    records = make_records(80)
    result  = run_shap(records, top_n_records=3)
    for rec in result.record_explanations:
        assert len(rec.feature_contributions) > 0
        assert rec.top_reason != ""


def test_shap_empty_records():
    result = run_shap([])
    assert result.global_importance == []
    assert result.record_explanations == []


def test_shap_too_few_records():
    records = make_records(8)   # below the 10-record minimum
    result  = run_shap(records)
    assert result.global_importance == []


def test_human_reason_non_empty():
    contribs = [
        {"feature": "cost_vs_rolling_mean_7", "shap_value": 0.8, "feature_value": 3.5},
        {"feature": "usage_quantity",         "shap_value": 0.4, "feature_value": 150.0},
    ]
    reason = _human_reason(contribs)
    assert len(reason) > 10
    assert "cost_vs_rolling_mean_7" in reason or "usage quantity" in reason


# ── Root Cause ────────────────────────────────────────────────────────────────

def test_root_cause_empty():
    rc = run_root_cause([], set())
    assert rc.total_anomaly_cost  == 0
    assert rc.total_anomaly_count == 0
    assert rc.by_service == []


def test_root_cause_no_anomalies():
    records = make_records(40)
    rc = run_root_cause(records, set())
    assert rc.total_anomaly_count == 0


def test_root_cause_breakdown_by_service():
    records   = make_multi_records(60)
    anom_ids  = {r.id for r in records[:20]}   # first 20 as anomalies
    rc = run_root_cause(records, anom_ids)
    assert len(rc.by_service) > 0


def test_root_cause_pct_sums_near_100():
    records  = make_records(60)
    anom_ids = {r.id for r in records[:30]}
    rc       = run_root_cause(records, anom_ids)
    if rc.by_service:
        total_pct = sum(d.pct for d in rc.by_service)
        assert abs(total_pct - 100.0) < 1.0


def test_root_cause_provider_breakdown():
    records  = make_multi_records(60)
    anom_ids = {r.id for r in records[:30]}
    rc       = run_root_cause(records, anom_ids)
    providers = [d.value for d in rc.by_provider]
    assert len(providers) > 0


def test_root_cause_top_chain_not_empty():
    records  = make_multi_records(60)
    anom_ids = {r.id for r in records[:30]}
    rc       = run_root_cause(records, anom_ids)
    assert len(rc.top_anomaly_chain) > 0


def test_root_cause_chain_has_cost():
    records  = make_multi_records(60)
    anom_ids = {r.id for r in records[:30]}
    rc       = run_root_cause(records, anom_ids)
    for chain in rc.top_anomaly_chain:
        assert "cost"  in chain
        assert "count" in chain


def test_root_cause_summary_non_empty():
    records  = make_multi_records(60)
    anom_ids = {r.id for r in records[:30]}
    rc       = run_root_cause(records, anom_ids)
    assert len(rc.summary) > 10


def test_root_cause_cost_matches_sum():
    records  = make_records(60)
    anom_ids = {r.id for r in records[:10]}
    rc       = run_root_cause(records, anom_ids)
    df       = records_to_dataframe(records)
    anom_df  = df[df["id"].isin(anom_ids)]
    expected = round(float(anom_df["total_cost"].sum()), 2)
    assert abs(rc.total_anomaly_cost - expected) < 0.01
