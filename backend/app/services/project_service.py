from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.organization import Organization
from app.schemas.project_schema import ProjectCreate
from app.repositories import project_repository


def _get_organization_or_raise(db: Session, organization_id: int) -> Organization:
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if org is None:
        raise ValueError(f"Organization with id {organization_id} not found.")
    return org


def create_project(
    db: Session,
    organization_id: int,
    project: ProjectCreate,
) -> Project:
    _get_organization_or_raise(db, organization_id)

    db_project = Project(
        name=project.name.strip(),
        description=project.description,
        organization_id=organization_id,
    )

    return project_repository.create(db, db_project)


def get_projects(db: Session, organization_id: int) -> list[Project]:
    _get_organization_or_raise(db, organization_id)
    return project_repository.get_all_by_org(db, organization_id)


def get_project(db: Session, organization_id: int, project_id: int) -> Project:
    _get_organization_or_raise(db, organization_id)

    db_project = project_repository.get_by_id(db, project_id)

    if db_project is None or db_project.organization_id != organization_id:
        raise ValueError(f"Project with id {project_id} not found.")

    return db_project


def update_project(
    db: Session,
    organization_id: int,
    project_id: int,
    project: ProjectCreate,
) -> Project:
    db_project = get_project(db, organization_id, project_id)

    db_project.name = project.name.strip()
    db_project.description = project.description

    return project_repository.update(db, db_project)


def delete_project(
    db: Session,
    organization_id: int,
    project_id: int,
) -> None:
    db_project = get_project(db, organization_id, project_id)
    project_repository.delete(db, db_project)
