from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta

from app.database.session import get_db
from app.models.organization import Organization
from app.models.billing import BillingRecord
from app.models.upload import Upload, UploadStatus

router = APIRouter(
    prefix="/organizations/{organization_id}/dashboard",
    tags=["Dashboard"],
)


def _get_org_or_404(db: Session, organization_id: int) -> Organization:
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if org is None:
        raise HTTPException(status_code=404, detail="Organization not found.")
    return org


@router.get("/summary")
def get_dashboard_summary(
    organization_id: int,
    db: Session = Depends(get_db),
):
    """
    Aggregated stats for the dashboard:
    - Total spend (all time + last 30d + prev 30d for % change)
    - Record count
    - Anomaly count
    - Provider breakdown
    - Daily spend for last 90 days (for the bar chart)
    - Top 5 services by cost
    """
    _get_org_or_404(db, organization_id)

    today     = date.today()
    last30    = today - timedelta(days=30)
    prev30    = today - timedelta(days=60)

    # ── Totals ────────────────────────────────────────────────────────────────
    total_spend = db.query(func.sum(BillingRecord.total_cost)).filter(
        BillingRecord.organization_id == organization_id
    ).scalar() or 0

    spend_last30 = db.query(func.sum(BillingRecord.total_cost)).filter(
        BillingRecord.organization_id == organization_id,
        BillingRecord.date >= last30,
    ).scalar() or 0

    spend_prev30 = db.query(func.sum(BillingRecord.total_cost)).filter(
        BillingRecord.organization_id == organization_id,
        BillingRecord.date >= prev30,
        BillingRecord.date < last30,
    ).scalar() or 0

    pct_change = 0.0
    if spend_prev30 > 0:
        pct_change = round((float(spend_last30) - float(spend_prev30)) / float(spend_prev30) * 100, 1)

    # ── Record + anomaly counts ───────────────────────────────────────────────
    record_count  = db.query(func.count(BillingRecord.id)).filter(
        BillingRecord.organization_id == organization_id
    ).scalar() or 0

    anomaly_count = db.query(func.count(BillingRecord.id)).filter(
        BillingRecord.organization_id == organization_id,
        BillingRecord.is_anomaly == True,  # noqa: E712
    ).scalar() or 0

    upload_count = db.query(func.count(Upload.id)).filter(
        Upload.organization_id == organization_id,
        Upload.status == UploadStatus.completed,
    ).scalar() or 0

    # ── Provider breakdown ────────────────────────────────────────────────────
    provider_rows = (
        db.query(BillingRecord.cloud_provider, func.sum(BillingRecord.total_cost))
        .filter(BillingRecord.organization_id == organization_id)
        .group_by(BillingRecord.cloud_provider)
        .all()
    )
    provider_breakdown = [
        {"provider": p, "total": round(float(t), 2)}
        for p, t in provider_rows
    ]

    # ── Daily spend last 90 days ──────────────────────────────────────────────
    last90 = today - timedelta(days=90)
    daily_rows = (
        db.query(BillingRecord.date, func.sum(BillingRecord.total_cost))
        .filter(
            BillingRecord.organization_id == organization_id,
            BillingRecord.date >= last90,
        )
        .group_by(BillingRecord.date)
        .order_by(BillingRecord.date)
        .all()
    )
    daily_spend = [
        {"date": str(d), "total": round(float(t), 2)}
        for d, t in daily_rows
    ]

    # ── Top services ──────────────────────────────────────────────────────────
    svc_rows = (
        db.query(BillingRecord.service, func.sum(BillingRecord.total_cost))
        .filter(BillingRecord.organization_id == organization_id)
        .group_by(BillingRecord.service)
        .order_by(func.sum(BillingRecord.total_cost).desc())
        .limit(6)
        .all()
    )
    total_svc = sum(float(t) for _, t in svc_rows) or 1
    top_services = [
        {
            "service": s,
            "total":   round(float(t), 2),
            "pct":     round(float(t) / total_svc * 100, 1),
        }
        for s, t in svc_rows
    ]

    # ── Recent anomalies ──────────────────────────────────────────────────────
    recent_anomalies_rows = (
        db.query(BillingRecord)
        .filter(
            BillingRecord.organization_id == organization_id,
            BillingRecord.is_anomaly == True,  # noqa: E712
        )
        .order_by(BillingRecord.date.desc())
        .limit(5)
        .all()
    )
    recent_anomalies = [
        {
            "date":           str(r.date),
            "service":        r.service,
            "cloud_provider": r.cloud_provider,
            "total_cost":     round(float(r.total_cost), 2),
            "anomaly_score":  round(float(r.anomaly_score or 0), 4),
        }
        for r in recent_anomalies_rows
    ]

    return {
        "total_spend":        round(float(total_spend), 2),
        "spend_last_30d":     round(float(spend_last30), 2),
        "spend_change_pct":   pct_change,
        "record_count":       record_count,
        "anomaly_count":      anomaly_count,
        "upload_count":       upload_count,
        "provider_breakdown": provider_breakdown,
        "daily_spend":        daily_spend,
        "top_services":       top_services,
        "recent_anomalies":   recent_anomalies,
    }
