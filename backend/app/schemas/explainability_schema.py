from typing import Optional
from pydantic import BaseModel, ConfigDict


class FeatureImportanceResponse(BaseModel):
    feature:    str
    importance: float
    direction:  str


class FeatureContributionResponse(BaseModel):
    feature:       str
    shap_value:    float
    feature_value: float


class RecordExplanationResponse(BaseModel):
    billing_record_id:     int
    date:                  str
    service:               str
    cloud_provider:        str
    total_cost:            float
    anomaly_score:         float
    feature_contributions: list[FeatureContributionResponse]
    top_reason:            str


class ShapResponse(BaseModel):
    global_importance:   list[FeatureImportanceResponse]
    record_explanations: list[RecordExplanationResponse]
    feature_names:       list[str]


# ── Root Cause ────────────────────────────────────────────────────────────────

class DimensionBreakdownResponse(BaseModel):
    dimension: str
    value:     str
    cost:      float
    count:     int
    pct:       float


class RootCauseResponse(BaseModel):
    total_anomaly_cost:  float
    total_anomaly_count: int
    by_service:          list[DimensionBreakdownResponse]
    by_provider:         list[DimensionBreakdownResponse]
    by_environment:      list[DimensionBreakdownResponse]
    by_region:           list[DimensionBreakdownResponse]
    by_department:       list[DimensionBreakdownResponse]
    top_anomaly_chain:   list[dict]
    summary:             str


# ── Combined explainability response ─────────────────────────────────────────

class ExplainabilityResponse(BaseModel):
    shap:       ShapResponse
    root_cause: RootCauseResponse
