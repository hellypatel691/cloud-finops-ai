from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.billing_schema import BillingRecordResponse
from app.repositories import billing_repository
from app.models.organization import Organization

router = APIRouter(
    prefix="/organizations/{organization_id}/billing",
    tags=["Billing"],
)


def _get_organization_or_raise(db: Session, organization_id: int) -> Organization:
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if org is None:
        raise HTTPException(status_code=404, detail=f"Organization with id {organization_id} not found.")
    return org


@router.get("/", response_model=list[BillingRecordResponse])
def read_billing(
    organization_id: int,
    db: Session = Depends(get_db),
):
    _get_organization_or_raise(db, organization_id)
    return billing_repository.get_all_by_org(db, organization_id)


@router.get("/upload/{upload_id}", response_model=list[BillingRecordResponse])
def read_billing_by_upload(
    organization_id: int,
    upload_id: int,
    db: Session = Depends(get_db),
):
    _get_organization_or_raise(db, organization_id)
    return billing_repository.get_by_upload(db, upload_id)
