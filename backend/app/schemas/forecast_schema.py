from typing import Optional
from pydantic import BaseModel, ConfigDict


class DailyForecastPointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ds:          str
    actual:      Optional[float]
    yhat:        float
    yhat_lower:  float
    yhat_upper:  float
    is_forecast: bool


class HorizonSummaryResponse(BaseModel):
    days:  int
    p10:   float
    p50:   float
    p90:   float
    total: float


class ModelMetricsResponse(BaseModel):
    name:     str
    mae:      Optional[float]
    mape:     Optional[float]
    selected: bool


class ProviderForecastResponse(BaseModel):
    provider: str
    p10_30d:  float
    p50_30d:  float
    p90_30d:  float


class ForecastResponse(BaseModel):
    series:                  list[DailyForecastPointResponse]
    horizons:                list[HorizonSummaryResponse]
    models:                  list[ModelMetricsResponse]
    selected_model:          str
    provider_breakdown:      list[ProviderForecastResponse]
    total_historical_spend:  float
    forecast_start:          str
