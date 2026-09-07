from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.organization_schema import (
    OrganizationCreate,
    OrganizationResponse,
)
from app.services.organization_service import (
    create_organization,
    get_organizations,
    get_organization,
    update_organization,
    delete_organization,
)

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.post(
    "/",
    response_model=OrganizationResponse,
    status_code=201,
)
def create(
    organization: OrganizationCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_organization(db, organization)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/",
    response_model=list[OrganizationResponse],
)
def read_all(
    db: Session = Depends(get_db),
):
    return get_organizations(db)


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def read_one(
    organization_id: int,
    db: Session = Depends(get_db),
):
    return get_organization(db, organization_id)


@router.put(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def update(
    organization_id: int,
    organization: OrganizationCreate,
    db: Session = Depends(get_db),
):
    try:
        return update_organization(db, organization_id, organization)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/{organization_id}",
    status_code=204,
)
def delete(
    organization_id: int,
    db: Session = Depends(get_db),
):
    delete_organization(db, organization_id)