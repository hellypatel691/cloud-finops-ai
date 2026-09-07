from datetime import date
from decimal import Decimal

from sqlalchemy import String, Integer, ForeignKey, Date, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class BillingRecord(Base):

    __tablename__ = "billing_records"

    id: Mapped[int] = mapped_column(primary_key=True)

    # ── Identity ──────────────────────────────────────────────────────────────
    date: Mapped[date] = mapped_column(Date, nullable=False)
    cloud_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    account_id: Mapped[str] = mapped_column(String(100), nullable=False)
    project_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── Organisation / grouping ───────────────────────────────────────────────
    environment: Mapped[str | None] = mapped_column(String(100), nullable=True)
    business_unit: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cost_center: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ── Service / resource ────────────────────────────────────────────────────
    service: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    unified_service_category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ── Usage & cost ─────────────────────────────────────────────────────────
    usage_quantity: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    unit_cost: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    discount_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    amortized_cost: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)

    # ── Budget / variance ─────────────────────────────────────────────────────
    budget_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    cost_variance: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)

    # ── Anomaly ───────────────────────────────────────────────────────────────
    anomaly_score: Mapped[Decimal | None] = mapped_column(Numeric(10, 6), nullable=True)
    is_anomaly: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    # ── Foreign keys ─────────────────────────────────────────────────────────
    organization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    upload_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("uploads.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    organization: Mapped["Organization"] = relationship(  # noqa: F821
        "Organization",
        back_populates="billing_records",
    )

    upload: Mapped["Upload"] = relationship(  # noqa: F821
        "Upload",
        back_populates="billing_records",
    )
