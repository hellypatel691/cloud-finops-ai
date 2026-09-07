from sqlalchemy.orm import Session

from app.models.project import Project


def get_by_id(db: Session, project_id: int) -> Project | None:
    return (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )


def get_all_by_org(db: Session, organization_id: int) -> list[Project]:
    return (
        db.query(Project)
        .filter(Project.organization_id == organization_id)
        .all()
    )


def create(db: Session, project: Project) -> Project:
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update(db: Session, project: Project) -> Project:
    db.commit()
    db.refresh(project)
    return project


def delete(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()
