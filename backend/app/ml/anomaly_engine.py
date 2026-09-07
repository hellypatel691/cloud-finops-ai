"""
Anomaly Detection Engine — orchestrates all detectors and
produces a unified result per billing record.

Pipeline:
  BillingRecords
      → features.py        (feature engineering)
      → statistical.py     (Z-score + IQR + seasonal)
      → isolation_forest.py
      → one_class_svm.py   (optional, skip if >10k rows for speed)
      → ensemble score     (weighted average)
      → AnomalyResult list
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from app.ml.features import records_to_dataframe
from app.ml.statistical import statistical_ensemble
from app.ml.isolation_forest import run_isolation_forest
from app.ml.one_class_svm import run_one_class_svm
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Threshold above which a record is classified as anomalous
ANOMALY_THRESHOLD = 0.55

# Skip OC-SVM for large datasets (too slow)
OC_SVM_MAX_ROWS = 10_000


@dataclass
class AnomalyResult:
    billing_record_id: int
    date:              str
    cloud_provider:    str
    service:           str
    environment:       str
    region:            str
    total_cost:        float
    anomaly_score:     float          # final ensemble score [0, 1]
    is_anomaly:        bool
    stat_score:        float
    if_score:          float
    svm_score:         Optional[float]
    anomaly_type:      str            # Spike | Drift | Seasonal | Normal


def _classify_type(row: pd.Series) -> str:
    score = row.get("anomaly_score", 0)
    if score < ANOMALY_THRESHOLD:
        return "Normal"
    # Heuristics based on which detector fired most
    if_s   = row.get("if_score", 0)
    stat_s = row.get("stat_score", 0)
    svm_s  = row.get("svm_score", 0) or 0
    # High stat + rolling deviation → Spike
    crm7 = row.get("cost_vs_rolling_mean_7", 1)
    if crm7 > 2.0:
        return "Spike"
    # Sustained elevation → Drift
    if stat_s > 0.5 and if_s > 0.5:
        return "Drift"
    # Seasonal pattern
    if stat_s > 0.4:
        return "Seasonal"
    return "Spike"


def run_anomaly_detection(records: list) -> list[AnomalyResult]:
    """
    Main entry point. Takes a list of BillingRecord ORM objects.
    Returns a list of AnomalyResult for ALL records (anomalous + normal).
    """
    logger.info("Running anomaly detection on %d records", len(records))

    df = records_to_dataframe(records)
    if df.empty:
        return []

    # ── 1. Statistical ────────────────────────────────────────────────────────
    df = statistical_ensemble(df)

    # ── 2. Isolation Forest ───────────────────────────────────────────────────
    df = run_isolation_forest(df)

    # ── 3. One-Class SVM (skip if too many rows) ──────────────────────────────
    use_svm = len(df) <= OC_SVM_MAX_ROWS
    if use_svm:
        df = run_one_class_svm(df)
    else:
        logger.info("Skipping OC-SVM — dataset too large (%d rows)", len(df))
        df["svm_score"]   = np.nan
        df["svm_anomaly"] = False

    # ── 4. Ensemble score ─────────────────────────────────────────────────────
    stat = df["stat_score"].fillna(0).values
    ifs  = df["if_score"].fillna(0).values
    svm  = df["svm_score"].fillna(0).values if use_svm else np.zeros(len(df))

    if use_svm:
        ensemble = 0.30 * stat + 0.40 * ifs + 0.30 * svm
    else:
        ensemble = 0.35 * stat + 0.65 * ifs

    df["anomaly_score"] = np.clip(ensemble, 0, 1)
    df["is_anomaly"]    = df["anomaly_score"] > ANOMALY_THRESHOLD

    logger.info(
        "Anomaly detection complete — %d / %d records flagged",
        df["is_anomaly"].sum(), len(df)
    )

    # ── 5. Build results ──────────────────────────────────────────────────────
    results: list[AnomalyResult] = []
    for _, row in df.iterrows():
        results.append(AnomalyResult(
            billing_record_id = int(row["id"]),
            date              = str(row["date"].date()),
            cloud_provider    = row["cloud_provider"],
            service           = row["service"],
            environment       = row["environment"],
            region            = row["region"],
            total_cost        = round(float(row["total_cost"]), 2),
            anomaly_score     = round(float(row["anomaly_score"]), 4),
            is_anomaly        = bool(row["is_anomaly"]),
            stat_score        = round(float(row.get("stat_score", 0)), 4),
            if_score          = round(float(row.get("if_score", 0)), 4),
            svm_score         = round(float(row["svm_score"]), 4) if use_svm else None,
            anomaly_type      = _classify_type(row),
        ))

    return results
