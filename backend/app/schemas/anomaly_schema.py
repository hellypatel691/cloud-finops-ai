from typing import Optional
from pydantic import BaseModel, ConfigDict


class AnomalyRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    billing_record_id: int
    date:              str
    cloud_provider:    str
    service:           str
    environment:       str
    region:            str
    total_cost:        float
    anomaly_score:     float
    is_anomaly:        bool
    stat_score:        float
    if_score:          float
    svm_score:         Optional[float]
    anomaly_type:      str


class AnomalySummaryResponse(BaseModel):
    total_records:   int
    total_anomalies: int
    anomaly_rate:    float
    avg_score:       float
    highest_cost:    float
    providers:       list[str]
    top_services:    list[dict]
    anomalies:       list[AnomalyRecordResponse]
