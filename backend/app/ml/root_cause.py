"""
Root Cause Attribution.

Takes anomalous billing records and traces each anomaly through
the attribution chain:

  Anomaly → Service → Resource Type → Team (Dept/BU) → Environment → Region

Returns a structured breakdown showing which dimensions are most
responsible for the cost spike, using both volume and cost-share analysis.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import defaultdict
from typing import Optional

import pandas as pd
import numpy as np

from app.ml.features import records_to_dataframe
from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class DimensionBreakdown:
    dimension: str          # e.g. "service", "environment"
    value:     str          # e.g. "EC2", "prod"
    cost:      float
    count:     int
    pct:       float        # % of total anomaly cost


@dataclass
class RootCauseResult:
    total_anomaly_cost:  float
    total_anomaly_count: int
    by_service:          list[DimensionBreakdown]
    by_provider:         list[DimensionBreakdown]
    by_environment:      list[DimensionBreakdown]
    by_region:           list[DimensionBreakdown]
    by_department:       list[DimensionBreakdown]
    top_anomaly_chain:   list[dict]   # [{service, env, region, cost, count}]
    summary:             str


def _breakdown(df: pd.DataFrame, col: str, total_cost: float) -> list[DimensionBreakdown]:
    """Group anomalous records by a dimension and compute cost share."""
    if col not in df.columns or df.empty:
        return []

    grouped = (
        df.groupby(col)
        .agg(cost=("total_cost", "sum"), count=(col, "count"))
        .reset_index()
        .sort_values("cost", ascending=False)
    )

    result = []
    for _, row in grouped.iterrows():
        result.append(DimensionBreakdown(
            dimension = col,
            value     = str(row[col]) if pd.notna(row[col]) else "unknown",
            cost      = round(float(row["cost"]), 2),
            count     = int(row["count"]),
            pct       = round(float(row["cost"]) / (total_cost + 1e-9) * 100, 1),
        ))
    return result


def _top_chains(df: pd.DataFrame, top_n: int = 10) -> list[dict]:
    """Find the most expensive (service, environment, region) combinations."""
    if df.empty:
        return []

    group_cols = [c for c in ["service", "environment", "region", "cloud_provider"] if c in df.columns]

    chains = (
        df.groupby(group_cols)
        .agg(cost=("total_cost", "sum"), count=("total_cost", "count"))
        .reset_index()
        .sort_values("cost", ascending=False)
        .head(top_n)
    )

    result = []
    for _, row in chains.iterrows():
        entry = {c: str(row[c]) if pd.notna(row[c]) else "unknown" for c in group_cols}
        entry["cost"]  = round(float(row["cost"]), 2)
        entry["count"] = int(row["count"])
        result.append(entry)

    return result


def _build_summary(rc: "RootCauseResult") -> str:
    """Produce a plain-English root cause summary."""
    if rc.total_anomaly_count == 0:
        return "No anomalies detected."

    parts = []

    if rc.by_service:
        top_svc = rc.by_service[0]
        parts.append(
            f"{top_svc.value} accounts for {top_svc.pct:.0f}% "
            f"of anomalous spend (${top_svc.cost:,.0f})."
        )

    if rc.by_environment:
        top_env = rc.by_environment[0]
        parts.append(
            f"Most anomalies occur in the {top_env.value} environment "
            f"({top_env.pct:.0f}% of cost)."
        )

    if rc.by_region:
        top_reg = rc.by_region[0]
        parts.append(f"Top region: {top_reg.value}.")

    if rc.top_anomaly_chain:
        chain = rc.top_anomaly_chain[0]
        svc   = chain.get("service", "?")
        env   = chain.get("environment", "?")
        reg   = chain.get("region", "?")
        cost  = chain["cost"]
        parts.append(
            f"Highest-impact combination: {svc} / {env} / {reg} "
            f"totalling ${cost:,.0f}."
        )

    return " ".join(parts) if parts else "Anomalies detected across multiple dimensions."


def run_root_cause(records: list, anomaly_record_ids: set[int]) -> RootCauseResult:
    """
    Attribute root causes for a set of anomalous billing records.

    Parameters
    ----------
    records           : ALL billing records for the org
    anomaly_record_ids: set of billing_record_id values flagged as anomalous

    Returns
    -------
    RootCauseResult with multi-dimensional cost breakdowns
    """
    logger.info(
        "Running root cause analysis — %d anomalies out of %d total records",
        len(anomaly_record_ids), len(records)
    )

    df = records_to_dataframe(records)
    if df.empty or not anomaly_record_ids:
        return RootCauseResult(
            total_anomaly_cost  = 0,
            total_anomaly_count = 0,
            by_service          = [],
            by_provider         = [],
            by_environment      = [],
            by_region           = [],
            by_department       = [],
            top_anomaly_chain   = [],
            summary             = "No anomalies to attribute.",
        )

    anom_df    = df[df["id"].isin(anomaly_record_ids)].copy()
    total_cost = float(anom_df["total_cost"].sum())
    total_cnt  = len(anom_df)

    # Add department column if available
    dept_col = None
    for r in records:
        if hasattr(r, "department") and r.department:
            dept_col = "department"
            break

    if dept_col:
        dept_vals = {r.id: (r.department or "unknown") for r in records}
        df["department"] = df["id"].map(dept_vals)
        anom_df["department"] = anom_df["id"].map(dept_vals)

    rc = RootCauseResult(
        total_anomaly_cost  = round(total_cost, 2),
        total_anomaly_count = total_cnt,
        by_service          = _breakdown(anom_df, "service",        total_cost),
        by_provider         = _breakdown(anom_df, "cloud_provider", total_cost),
        by_environment      = _breakdown(anom_df, "environment",    total_cost),
        by_region           = _breakdown(anom_df, "region",         total_cost),
        by_department       = _breakdown(anom_df, "department",     total_cost) if dept_col else [],
        top_anomaly_chain   = _top_chains(anom_df),
        summary             = "",
    )
    rc.summary = _build_summary(rc)

    logger.info("Root cause complete — %s", rc.summary[:80])
    return rc
