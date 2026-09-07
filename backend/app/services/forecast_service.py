from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.repositories import billing_repository
from app.ml.forecast_engine import run_forecast, ForecastResult
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _get_org_or_raise(db: Session, organization_id: int) -> Organization:
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if org is None:
        raise ValueError(f"Organization with id {organization_id} not found.")
    return org


def get_forecast(db: Session, organization_id: int) -> dict:
    """
    Run the full forecasting pipeline (Prophet + LightGBM)
    on all billing records for an organization.
    """
    _get_org_or_raise(db, organization_id)

    records = billing_repository.get_all_by_org(db, organization_id)

    result: ForecastResult = run_forecast(records)

    return {
        "series":                 [vars(p) for p in result.series],
        "horizons":               [vars(h) for h in result.horizons],
        "models":                 [vars(m) for m in result.models],
        "selected_model":         result.selected_model,
        "provider_breakdown":     [vars(p) for p in result.provider_breakdown],
        "total_historical_spend": result.total_historical_spend,
        "forecast_start":         result.forecast_start,
    }
