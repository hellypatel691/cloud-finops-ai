from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.project_schema import ProjectCreate, ProjectResponse
from app.services.project_service import (
    create_project,
    get_projects,
    get_project,
    update_project,
    delete_project,
)

router = APIRouter(
    prefix="/organizations/{organization_id}/projects",
    tags=["Projects"],
)


@router.post("/", response_model=ProjectResponse, status_code=201)
def create(
    organization_id: int,
    project: ProjectCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_project(db, organization_id, project)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/", response_model=list[ProjectResponse])
def read_all(
    organization_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_projects(db, organization_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{project_id}", response_model=ProjectResponse)
def read_one(
    organization_id: int,
    project_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_project(db, organization_id, project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{project_id}", response_model=ProjectResponse)
def update(
    organization_id: int,
    project_id: int,
    project: ProjectCreate,
    db: Session = Depends(get_db),
):
    try:
        return update_project(db, organization_id, project_id, project)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{project_id}", status_code=204)
def delete(
    organization_id: int,
    project_id: int,
    db: Session = Depends(get_db),
):
    try:
        delete_project(db, organization_id, project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
