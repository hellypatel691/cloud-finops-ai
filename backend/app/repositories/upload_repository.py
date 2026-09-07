from sqlalchemy.orm import Session

from app.models.upload import Upload


def get_by_id(db: Session, upload_id: int) -> Upload | None:
    return db.query(Upload).filter(Upload.id == upload_id).first()


def get_all_by_org(db: Session, organization_id: int) -> list[Upload]:
    return (
        db.query(Upload)
        .filter(Upload.organization_id == organization_id)
        .order_by(Upload.created_at.desc())
        .all()
    )


def create(db: Session, upload: Upload) -> Upload:
    db.add(upload)
    db.commit()
    db.refresh(upload)
    return upload


def update(db: Session, upload: Upload) -> Upload:
    db.commit()
    db.refresh(upload)
    return upload
