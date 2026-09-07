from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.explainability_schema import ExplainabilityResponse
from app.services.explainability_service import get_explainability

router = APIRouter(
    prefix="/organizations/{organization_id}/explainability",
    tags=["Explainability"],
)


@router.get("/", response_model=ExplainabilityResponse)
def explainability(
    organization_id: int,
    db: Session = Depends(get_db),
):
    """
    Run SHAP + root cause attribution on all billing records for an org.

    Returns:
    - Global feature importance (mean |SHAP| values)
    - Per-record explanations for top anomalies
    - Multi-dimensional root cause breakdown
      (by service, provider, environment, region, department)
    """
    try:
        return get_explainability(db, organization_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
