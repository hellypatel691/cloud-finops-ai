from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Organization(Base):

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    projects: Mapped[list["Project"]] = relationship(  # noqa: F821
        "Project",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    uploads: Mapped[list["Upload"]] = relationship(  # noqa: F821
        "Upload",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    billing_records: Mapped[list["BillingRecord"]] = relationship(  # noqa: F821
        "BillingRecord",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    members: Mapped[list["OrganizationMember"]] = relationship(  # noqa: F821
        "OrganizationMember",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
