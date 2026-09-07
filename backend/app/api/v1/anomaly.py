from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.anomaly_schema import AnomalySummaryResponse
from app.services.anomaly_service import detect_anomalies

router = APIRouter(
    prefix="/organizations/{organization_id}/anomalies",
    tags=["Anomalies"],
)


@router.get("/", response_model=AnomalySummaryResponse)
def get_anomalies(
    organization_id: int,
    db: Session = Depends(get_db),
):
    """
    Run anomaly detection on all billing records for an organization.
    Uses Z-score + IQR + Seasonal + Isolation Forest + One-Class SVM ensemble.
    """
    try:
        return detect_anomalies(db, organization_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
