from sqlalchemy.orm import Session

from app.models.organization import Organization


def get_by_id(db: Session, organization_id: int) -> Organization | None:
    return (
        db.query(Organization)
        .filter(Organization.id == organization_id)
        .first()
    )


def get_by_name(db: Session, name: str) -> Organization | None:
    return (
        db.query(Organization)
        .filter(Organization.name == name)
        .first()
    )


def get_all(db: Session) -> list[Organization]:
    return db.query(Organization).all()


def create(db: Session, organization: Organization) -> Organization:
    db.add(organization)
    db.commit()
    db.refresh(organization)
    return organization


def update(db: Session, organization: Organization) -> Organization:
    db.commit()
    db.refresh(organization)
    return organization


def delete(db: Session, organization: Organization) -> None:
    db.delete(organization)
    db.commit()
