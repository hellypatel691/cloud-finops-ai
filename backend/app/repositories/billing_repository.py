from sqlalchemy.orm import Session

from app.models.billing import BillingRecord


def bulk_insert(db: Session, records: list[BillingRecord]) -> None:
    db.bulk_save_objects(records)
    db.commit()


def get_all_by_org(db: Session, organization_id: int) -> list[BillingRecord]:
    return (
        db.query(BillingRecord)
        .filter(BillingRecord.organization_id == organization_id)
        .order_by(BillingRecord.date.asc())
        .all()
    )


def get_by_upload(db: Session, upload_id: int) -> list[BillingRecord]:
    return (
        db.query(BillingRecord)
        .filter(BillingRecord.upload_id == upload_id)
        .all()
    )
