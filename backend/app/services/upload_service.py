import io
from decimal import Decimal, InvalidOperation

import pandas as pd
from sqlalchemy.orm import Session

from app.models.upload import Upload, UploadStatus
from app.models.billing import BillingRecord
from app.models.organization import Organization
from app.repositories import upload_repository, billing_repository
from app.utils.csv_validator import validate_csv
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _get_organization_or_raise(db: Session, organization_id: int) -> Organization:
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if org is None:
        raise ValueError(f"Organization with id {organization_id} not found.")
    return org


def _safe_decimal(value) -> Decimal | None:
    try:
        if pd.isna(value):
            return None
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        return None


def _safe_str(value) -> str | None:
    if pd.isna(value):
        return None
    return str(value).strip() or None


def create_upload(
    db: Session,
    organization_id: int,
    file_bytes: bytes,
    filename: str,
    project_id: int | None = None,
) -> Upload:
    _get_organization_or_raise(db, organization_id)

    # ── Validate ──────────────────────────────────────────────────────────────
    result = validate_csv(file_bytes, filename)

    upload = Upload(
        filename=filename,
        status=UploadStatus.pending,
        organization_id=organization_id,
        project_id=project_id,
    )

    upload_repository.create(db, upload)

    if not result.valid:
        upload.status = UploadStatus.failed
        upload.error_message = "; ".join(result.errors)
        upload_repository.update(db, upload)
        raise ValueError(f"CSV validation failed: {'; '.join(result.errors)}")

    # ── Process ───────────────────────────────────────────────────────────────
    upload.status = UploadStatus.processing
    upload_repository.update(db, upload)

    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
        df["date"] = pd.to_datetime(df["date"])

        records: list[BillingRecord] = []

        for _, row in df.iterrows():
            records.append(
                BillingRecord(
                    date=row["date"].date(),
                    cloud_provider=str(row["cloud_provider"]),
                    account_id=str(row["account_id"]),
                    project_name=_safe_str(row.get("project_id")),
                    environment=_safe_str(row.get("environment")),
                    business_unit=_safe_str(row.get("business_unit")),
                    department=_safe_str(row.get("department")),
                    cost_center=_safe_str(row.get("cost_center")),
                    region=_safe_str(row.get("region")),
                    service=str(row["service"]),
                    resource_type=_safe_str(row.get("resource_type")),
                    usage_quantity=_safe_decimal(row.get("usage_quantity")),
                    unit_cost=_safe_decimal(row.get("list_cost")),
                    total_cost=_safe_decimal(row.get("net_cost")) or Decimal("0"),
                    discount_amount=_safe_decimal(row.get("discount_amount")),
                    amortized_cost=_safe_decimal(row.get("amortized_cost")),
                    budget_amount=_safe_decimal(row.get("budget_amount")),
                    cost_variance=_safe_decimal(row.get("cost_variance_7d_pct")),
                    anomaly_score=_safe_decimal(row.get("anomaly_score")),
                    is_anomaly=bool(row["is_anomaly"]) if "is_anomaly" in row and not pd.isna(row.get("is_anomaly")) else None,
                    organization_id=organization_id,
                    upload_id=upload.id,
                )
            )

        billing_repository.bulk_insert(db, records)

        upload.status = UploadStatus.completed
        upload.row_count = len(records)
        upload_repository.update(db, upload)

        logger.info(
            "Upload %d completed: %d billing records ingested for org %d",
            upload.id,
            len(records),
            organization_id,
        )

    except Exception as exc:
        logger.error("Upload %d failed during processing: %s", upload.id, str(exc))
        upload.status = UploadStatus.failed
        upload.error_message = str(exc)
        upload_repository.update(db, upload)
        raise

    return upload


def get_uploads(db: Session, organization_id: int) -> list[Upload]:
    _get_organization_or_raise(db, organization_id)
    return upload_repository.get_all_by_org(db, organization_id)


def get_upload(db: Session, organization_id: int, upload_id: int) -> Upload:
    _get_organization_or_raise(db, organization_id)

    upload = upload_repository.get_by_id(db, upload_id)

    if upload is None or upload.organization_id != organization_id:
        raise ValueError(f"Upload with id {upload_id} not found.")

    return upload
