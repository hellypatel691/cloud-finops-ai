"""
SHAP Explainability for the Isolation Forest anomaly detector.

Uses TreeExplainer (fast, exact for tree-based models) to compute
per-feature SHAP values for every anomalous record.

Output:
  - Global feature importance (mean |SHAP|)
  - Per-record feature contributions for the top anomalies
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from app.ml.features import (
    records_to_dataframe,
    engineer_features,
    get_feature_matrix,
    FEATURE_COLS,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class FeatureImportance:
    feature:    str
    importance: float          # mean |SHAP| across anomalies, normalised 0-100
    direction:  str            # "increases_risk" | "decreases_risk" | "neutral"


@dataclass
class RecordExplanation:
    billing_record_id:     int
    date:                  str
    service:               str
    cloud_provider:        str
    total_cost:            float
    anomaly_score:         float
    feature_contributions: list[dict]
    top_reason:            str


@dataclass
class ShapResult:
    global_importance:   list[FeatureImportance]
    record_explanations: list[RecordExplanation]
    feature_names:       list[str]


def _human_reason(contributions: list[dict]) -> str:
    """Turn the top SHAP drivers into a plain-English sentence."""
    top = sorted(contributions, key=lambda x: abs(x["shap_value"]), reverse=True)[:2]
    if not top:
        return "Anomaly detected by ensemble model."

    parts = []
    for c in top:
        feat = c["feature"].replace("_", " ")
        val  = c["feature_value"]
        if c["shap_value"] > 0:
            parts.append(f"high {feat} ({val:.2f})")
        else:
            parts.append(f"low {feat} ({val:.2f})")

    return "Driven by " + " and ".join(parts) + "."


def run_shap(
    records: list,
    top_n_records: int = 20,
) -> ShapResult:
    """
    Compute SHAP values for anomalous billing records.

    Parameters
    ----------
    records       : list of BillingRecord ORM objects
    top_n_records : max number of individual record explanations to return

    Returns
    -------
    ShapResult with global importance + per-record explanations
    """
    import shap
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler

    logger.info("Running SHAP on %d records", len(records))

    df = records_to_dataframe(records)
    if df.empty or len(df) < 10:
        logger.warning("Not enough data for SHAP")
        return ShapResult([], [], FEATURE_COLS)

    df   = engineer_features(df)
    X    = get_feature_matrix(df)
    available_features = [c for c in FEATURE_COLS if c in df.columns]

    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Re-fit Isolation Forest (same params as anomaly engine)
    clf = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_scaled)

    # ── SHAP TreeExplainer ────────────────────────────────────────────────────
    try:
        explainer   = shap.TreeExplainer(clf)
        shap_values = explainer.shap_values(X_scaled)
    except Exception as e:
        logger.error("TreeExplainer failed: %s — falling back to KernelExplainer", e)
        background  = shap.sample(X_scaled, min(100, len(X_scaled)))
        explainer   = shap.KernelExplainer(clf.decision_function, background)
        shap_values = explainer.shap_values(X_scaled, nsamples=50)

    shap_arr = np.array(shap_values)    # (n, features)

    # ── Anomaly mask ─────────────────────────────────────────────────────────
    preds        = clf.predict(X_scaled)
    anomaly_mask = preds == -1
    n_anomalies  = anomaly_mask.sum()
    logger.info("SHAP computed — %d anomalies", n_anomalies)

    # ── Global feature importance ─────────────────────────────────────────────
    shap_for_imp = shap_arr[anomaly_mask] if n_anomalies > 0 else shap_arr
    mean_abs     = np.abs(shap_for_imp).mean(axis=0)
    total        = mean_abs.sum() + 1e-9
    norm_imp     = (mean_abs / total * 100).tolist()
    mean_shap    = shap_for_imp.mean(axis=0).tolist()

    global_importance = []
    for feat, imp, ms in zip(available_features, norm_imp, mean_shap):
        if ms > 0.01:
            direction = "increases_risk"
        elif ms < -0.01:
            direction = "decreases_risk"
        else:
            direction = "neutral"
        global_importance.append(FeatureImportance(
            feature   = feat,
            importance = round(imp, 2),
            direction  = direction,
        ))
    global_importance.sort(key=lambda x: x.importance, reverse=True)

    # ── Per-record explanations ───────────────────────────────────────────────
    raw_scores  = clf.decision_function(X_scaled)
    flipped     = -raw_scores
    min_s, max_s = flipped.min(), flipped.max()
    norm_scores  = (flipped - min_s) / (max_s - min_s + 1e-9)

    anomaly_indices = np.where(anomaly_mask)[0]
    top_indices = sorted(
        anomaly_indices,
        key=lambda i: norm_scores[i],
        reverse=True,
    )[:top_n_records]

    record_explanations = []
    for idx in top_indices:
        row  = df.iloc[idx]
        sv   = shap_arr[idx]

        contributions = [
            {
                "feature":       feat,
                "shap_value":    round(float(sv[j]), 4),
                "feature_value": round(float(X[idx, j]), 4),
            }
            for j, feat in enumerate(available_features)
        ]
        contributions.sort(key=lambda c: abs(c["shap_value"]), reverse=True)

        record_explanations.append(RecordExplanation(
            billing_record_id    = int(row["id"]),
            date                 = str(row["date"].date()),
            service              = str(row["service"]),
            cloud_provider       = str(row["cloud_provider"]),
            total_cost           = round(float(row["total_cost"]), 2),
            anomaly_score        = round(float(norm_scores[idx]), 4),
            feature_contributions= contributions[:8],
            top_reason           = _human_reason(contributions[:3]),
        ))

    return ShapResult(
        global_importance   = global_importance,
        record_explanations = record_explanations,
        feature_names       = available_features,
    )
