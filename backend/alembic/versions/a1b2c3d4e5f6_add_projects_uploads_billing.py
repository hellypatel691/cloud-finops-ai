"""add projects, uploads, billing_records tables

Revision ID: a1b2c3d4e5f6
Revises: 13903769f767
Create Date: 2026-08-10 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "13903769f767"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── projects ──────────────────────────────────────────────────────────────
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── uploads ───────────────────────────────────────────────────────────────
    op.create_table(
        "uploads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "processing", "completed", "failed", name="uploadstatus"),
            nullable=False,
        ),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.String(length=1000), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── billing_records ───────────────────────────────────────────────────────
    op.create_table(
        "billing_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("cloud_provider", sa.String(length=50), nullable=False),
        sa.Column("account_id", sa.String(length=100), nullable=False),
        sa.Column("project_name", sa.String(length=255), nullable=True),
        sa.Column("environment", sa.String(length=100), nullable=True),
        sa.Column("business_unit", sa.String(length=100), nullable=True),
        sa.Column("department", sa.String(length=100), nullable=True),
        sa.Column("cost_center", sa.String(length=100), nullable=True),
        sa.Column("region", sa.String(length=100), nullable=True),
        sa.Column("service", sa.String(length=255), nullable=False),
        sa.Column("resource_type", sa.String(length=255), nullable=True),
        sa.Column("unified_service_category", sa.String(length=100), nullable=True),
        sa.Column("usage_quantity", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("unit_cost", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column("total_cost", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("discount_amount", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("amortized_cost", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("budget_amount", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("cost_variance", sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column("anomaly_score", sa.Numeric(precision=10, scale=6), nullable=True),
        sa.Column("is_anomaly", sa.Boolean(), nullable=True),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("upload_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["upload_id"], ["uploads.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── indexes ───────────────────────────────────────────────────────────────
    op.create_index("ix_billing_org_date", "billing_records", ["organization_id", "date"])
    op.create_index("ix_billing_provider", "billing_records", ["cloud_provider"])
    op.create_index("ix_billing_upload", "billing_records", ["upload_id"])


def downgrade() -> None:
    op.drop_index("ix_billing_upload", table_name="billing_records")
    op.drop_index("ix_billing_provider", table_name="billing_records")
    op.drop_index("ix_billing_org_date", table_name="billing_records")
    op.drop_table("billing_records")
    op.drop_table("uploads")
    op.drop_table("projects")
    op.execute("DROP TYPE IF EXISTS uploadstatus")
