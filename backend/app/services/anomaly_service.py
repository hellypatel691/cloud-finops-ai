from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.repositories import billing_repository
from app.ml.anomaly_engine import run_anomaly_detection, AnomalyResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _get_org_or_raise(db: Session, organization_id: int) -> Organization:
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if org is None:
        raise ValueError(f"Organization with id {organization_id} not found.")
    return org


def detect_anomalies(db: Session, organization_id: int) -> dict:
    """
    Run the full anomaly detection pipeline on all billing records
    for an organization and return a summary + detail list.
    """
    _get_org_or_raise(db, organization_id)

    records = billing_repository.get_all_by_org(db, organization_id)

    if not records:
        return {
            "total_records":   0,
            "total_anomalies": 0,
            "anomaly_rate":    0.0,
            "avg_score":       0.0,
            "highest_cost":    0.0,
            "providers":       [],
            "top_services":    [],
            "anomalies":       [],
        }

    results: list[AnomalyResult] = run_anomaly_detection(records)

    anomalies   = [r for r in results if r.is_anomaly]
    total       = len(results)
    n_anomalies = len(anomalies)
    avg_score   = sum(r.anomaly_score for r in anomalies) / n_anomalies if n_anomalies else 0.0
    highest     = max((r.total_cost for r in anomalies), default=0.0)
    providers   = list({r.cloud_provider for r in anomalies})

    # Top services by anomaly count
    from collections import Counter
    svc_counts = Counter(r.service for r in anomalies)
    top_services = [
        {"service": svc, "count": cnt}
        for svc, cnt in svc_counts.most_common(10)
    ]

    return {
        "total_records":   total,
        "total_anomalies": n_anomalies,
        "anomaly_rate":    round(n_anomalies / total, 4) if total else 0.0,
        "avg_score":       round(avg_score, 4),
        "highest_cost":    round(highest, 2),
        "providers":       sorted(providers),
        "top_services":    top_services,
        "anomalies":       [vars(a) for a in anomalies],
    }
