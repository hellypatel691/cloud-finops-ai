from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.organization import Organization
from app.schemas.organization_schema import OrganizationCreate


def create_organization(
    db: Session,
    organization: OrganizationCreate,
) -> Organization:

    db_org = Organization(
        name=organization.name.strip(),
        description=organization.description,
    )

    try:
        db.add(db_org)
        db.commit()
        db.refresh(db_org)
        return db_org

    except IntegrityError:
        db.rollback()
        raise ValueError("An organization with this name already exists.")


def get_organizations(db: Session) -> list[Organization]:
    return db.query(Organization).all()


def get_organization(db: Session, organization_id: int) -> Organization:
    db_org = (
        db.query(Organization)
        .filter(Organization.id == organization_id)
        .first()
    )

    if db_org is None:
        raise ValueError(f"Organization with id {organization_id} not found.")

    return db_org


def update_organization(
    db: Session,
    organization_id: int,
    organization: OrganizationCreate,
) -> Organization:

    db_org = (
        db.query(Organization)
        .filter(Organization.id == organization_id)
        .first()
    )

    if db_org is None:
        raise ValueError(f"Organization with id {organization_id} not found.")

    db_org.name = organization.name.strip()
    db_org.description = organization.description

    try:
        db.commit()
        db.refresh(db_org)
        return db_org

    except IntegrityError:
        db.rollback()
        raise ValueError("An organization with this name already exists.")


def delete_organization(db: Session, organization_id: int) -> None:

    db_org = (
        db.query(Organization)
        .filter(Organization.id == organization_id)
        .first()
    )

    if db_org is None:
        raise ValueError(f"Organization with id {organization_id} not found.")

    db.delete(db_org)
    db.commit()
