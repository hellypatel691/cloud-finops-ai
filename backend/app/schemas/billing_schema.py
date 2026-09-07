from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class BillingRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date
    cloud_provider: str
    account_id: str
    project_name: str | None
    environment: str | None
    business_unit: str | None
    department: str | None
    cost_center: str | None
    region: str | None
    service: str
    resource_type: str | None
    unified_service_category: str | None
    usage_quantity: Decimal | None
    unit_cost: Decimal | None
    total_cost: Decimal
    discount_amount: Decimal | None
    amortized_cost: Decimal | None
    budget_amount: Decimal | None
    cost_variance: Decimal | None
    anomaly_score: Decimal | None
    is_anomaly: bool | None
    organization_id: int
    upload_id: int
