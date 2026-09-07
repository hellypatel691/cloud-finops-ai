from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.repositories import billing_repository
from app.ml.anomaly_engine import run_anomaly_detection
from app.ml.shap_explainer import run_shap
from app.ml.root_cause import run_root_cause
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _get_org_or_raise(db: Session, organization_id: int) -> Organization:
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if org is None:
        raise ValueError(f"Organization with id {organization_id} not found.")
    return org


def get_explainability(db: Session, organization_id: int) -> dict:
    """
    Run full explainability pipeline:
      1. Anomaly detection  → identify anomalous record IDs
      2. SHAP               → global importance + per-record explanations
      3. Root cause         → multi-dimension cost attribution

    Returns a combined dict matching ExplainabilityResponse.
    """
    _get_org_or_raise(db, organization_id)

    records = billing_repository.get_all_by_org(db, organization_id)

    if not records:
        empty_shap = {
            "global_importance":   [],
            "record_explanations": [],
            "feature_names":       [],
        }
        empty_rc = {
            "total_anomaly_cost":  0,
            "total_anomaly_count": 0,
            "by_service":          [],
            "by_provider":         [],
            "by_environment":      [],
            "by_region":           [],
            "by_department":       [],
            "top_anomaly_chain":   [],
            "summary":             "No billing data available.",
        }
        return {"shap": empty_shap, "root_cause": empty_rc}

    # ── Step 1: Anomaly detection ─────────────────────────────────────────────
    logger.info("Step 1 — anomaly detection for org %d", organization_id)
    anomaly_results = run_anomaly_detection(records)
    anomaly_ids     = {r.billing_record_id for r in anomaly_results if r.is_anomaly}

    # ── Step 2: SHAP ──────────────────────────────────────────────────────────
    logger.info("Step 2 — SHAP explainability for org %d", organization_id)
    shap_result = run_shap(records, top_n_records=20)

    shap_dict = {
        "global_importance": [vars(f) for f in shap_result.global_importance],
        "record_explanations": [
            {
                **vars(r),
                "feature_contributions": r.feature_contributions,
            }
            for r in shap_result.record_explanations
        ],
        "feature_names": shap_result.feature_names,
    }

    # ── Step 3: Root cause ────────────────────────────────────────────────────
    logger.info("Step 3 — root cause attribution for org %d", organization_id)
    rc_result = run_root_cause(records, anomaly_ids)

    rc_dict = {
        "total_anomaly_cost":  rc_result.total_anomaly_cost,
        "total_anomaly_count": rc_result.total_anomaly_count,
        "by_service":     [vars(d) for d in rc_result.by_service],
        "by_provider":    [vars(d) for d in rc_result.by_provider],
        "by_environment": [vars(d) for d in rc_result.by_environment],
        "by_region":      [vars(d) for d in rc_result.by_region],
        "by_department":  [vars(d) for d in rc_result.by_department],
        "top_anomaly_chain": rc_result.top_anomaly_chain,
        "summary":           rc_result.summary,
    }

    return {"shap": shap_dict, "root_cause": rc_dict}
