import io
from dataclasses import dataclass

import pandas as pd

# Columns that must be present in every uploaded billing CSV
REQUIRED_COLUMNS: set[str] = {
    "date",
    "cloud_provider",
    "account_id",
    "service",
    "net_cost",
}

# Full expected column set (superset — extras are allowed)
KNOWN_COLUMNS: set[str] = {
    "date", "year", "month", "day", "day_of_week",
    "is_month_start", "is_month_end",
    "cloud_provider", "account_id", "project_id",
    "environment", "business_unit", "department", "cost_center", "region",
    "service", "resource_type",
    "usage_quantity", "usage_unit",
    "list_cost", "savings_plan_coverage_pct", "reserved_instance_coverage_pct",
    "discount_rate_pct", "discount_amount", "net_cost", "on_demand_cost",
    "reserved_savings", "savings_plan_savings", "spot_savings",
    "amortized_cost", "forecast_monthly_cost",
    "budget_amount", "budget_utilization_pct", "budget_status",
    "cost_variance_7d_pct", "cost_variance_30d_pct",
    "anomaly_score", "is_anomaly",
    "currency", "tags",
}

VALID_PROVIDERS: set[str] = {"AWS", "Azure", "GCP"}
MAX_FILE_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    row_count: int = 0


def validate_csv(file_bytes: bytes, filename: str) -> ValidationResult:
    errors: list[str] = []

    # ── File size ─────────────────────────────────────────────────────────────
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        return ValidationResult(
            valid=False,
            errors=["File exceeds maximum allowed size of 50 MB."],
        )

    # ── Extension ─────────────────────────────────────────────────────────────
    if not filename.lower().endswith(".csv"):
        errors.append("File must have a .csv extension.")

    # ── Parse ─────────────────────────────────────────────────────────────────
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
    except Exception as exc:
        return ValidationResult(
            valid=False,
            errors=[f"Could not parse CSV: {exc}"],
        )

    if df.empty:
        return ValidationResult(valid=False, errors=["CSV file is empty."])

    # ── Required columns ──────────────────────────────────────────────────────
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        errors.append(f"Missing required columns: {sorted(missing)}")

    # ── Provider values ───────────────────────────────────────────────────────
    if "cloud_provider" in df.columns:
        invalid_providers = set(df["cloud_provider"].dropna().unique()) - VALID_PROVIDERS
        if invalid_providers:
            errors.append(
                f"Unknown cloud_provider values: {sorted(invalid_providers)}. "
                f"Expected one of {sorted(VALID_PROVIDERS)}."
            )

    # ── Date column ───────────────────────────────────────────────────────────
    if "date" in df.columns:
        try:
            pd.to_datetime(df["date"])
        except Exception:
            errors.append("Column 'date' contains values that cannot be parsed as dates.")

    # ── net_cost must be numeric ──────────────────────────────────────────────
    if "net_cost" in df.columns:
        if not pd.api.types.is_numeric_dtype(df["net_cost"]):
            errors.append("Column 'net_cost' must contain numeric values.")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        row_count=len(df),
    )
