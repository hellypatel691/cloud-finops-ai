from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.forecast_schema import ForecastResponse
from app.services.forecast_service import get_forecast

router = APIRouter(
    prefix="/organizations/{organization_id}/forecast",
    tags=["Forecast"],
)


@router.get("/", response_model=ForecastResponse)
def forecast(
    organization_id: int,
    db: Session = Depends(get_db),
):
    """
    Run Prophet + LightGBM ensemble forecast on all billing records
    for an organization. Returns 7/30/90-day horizon summaries,
    daily series with confidence bands, and model comparison metrics.
    """
    try:
        return get_forecast(db, organization_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
