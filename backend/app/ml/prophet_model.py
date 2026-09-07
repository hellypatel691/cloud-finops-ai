"""
Prophet time-series forecasting.
Handles seasonality, holidays, and uncertainty intervals.
"""
from __future__ import annotations

import warnings
import pandas as pd
import numpy as np

from app.utils.logger import get_logger

logger = get_logger(__name__)


def run_prophet(
    daily: pd.DataFrame,
    horizon_days: int = 90,
    interval_width: float = 0.80,
) -> pd.DataFrame:
    """
    Fit Prophet on a daily spend series and forecast `horizon_days` ahead.

    Parameters
    ----------
    daily         : DataFrame with columns ds (datetime), y (float)
    horizon_days  : number of days to forecast
    interval_width: confidence interval width (0.8 = 80%)

    Returns
    -------
    DataFrame with columns:
        ds, yhat, yhat_lower, yhat_upper, is_forecast (bool)
    """
    # Suppress Stan / cmdstan output
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from prophet import Prophet  # import here to avoid slow startup

    if daily.empty or len(daily) < 14:
        logger.warning("Not enough data for Prophet (need ≥14 days, got %d)", len(daily))
        return pd.DataFrame(columns=["ds", "yhat", "yhat_lower", "yhat_upper", "is_forecast"])

    logger.info("Fitting Prophet on %d days, forecasting %d days ahead", len(daily), horizon_days)

    train = daily[["ds", "y"]].copy()
    train["ds"] = pd.to_datetime(train["ds"])

    m = Prophet(
        interval_width=interval_width,
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m.fit(train)

    future = m.make_future_dataframe(periods=horizon_days, freq="D")
    forecast = m.predict(future)

    last_train_date = train["ds"].max()

    result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    result["yhat"]       = result["yhat"].clip(lower=0)
    result["yhat_lower"] = result["yhat_lower"].clip(lower=0)
    result["yhat_upper"] = result["yhat_upper"].clip(lower=0)
    result["is_forecast"] = result["ds"] > last_train_date

    logger.info("Prophet complete — %d historical + %d forecast rows",
                (~result["is_forecast"]).sum(), result["is_forecast"].sum())

    return result
