"""
LightGBM feature-based forecasting.
Uses lag and rolling features to predict future daily spend.
"""
from __future__ import annotations

import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.metrics import mean_absolute_error

from app.ml.forecast_features import add_lgbm_features, LGBM_FEATURE_COLS
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _train_eval(
    df: pd.DataFrame,
    val_size: int = 30,
) -> tuple[lgb.Booster, float]:
    """Train LightGBM and return model + MAE on validation split."""
    df = add_lgbm_features(df)

    split = len(df) - val_size
    train = df.iloc[:split]
    val   = df.iloc[split:]

    X_train = train[LGBM_FEATURE_COLS].values
    y_train = train["y"].values
    X_val   = val[LGBM_FEATURE_COLS].values
    y_val   = val["y"].values

    dtrain = lgb.Dataset(X_train, label=y_train)
    dval   = lgb.Dataset(X_val,   label=y_val, reference=dtrain)

    params = {
        "objective":        "regression_l1",
        "metric":           "mae",
        "learning_rate":    0.05,
        "num_leaves":       31,
        "feature_fraction": 0.8,
        "bagging_fraction": 0.8,
        "bagging_freq":     5,
        "verbose":          -1,
        "n_jobs":           -1,
    }

    callbacks = [lgb.early_stopping(50, verbose=False), lgb.log_evaluation(period=-1)]

    model = lgb.train(
        params,
        dtrain,
        num_boost_round=500,
        valid_sets=[dval],
        callbacks=callbacks,
    )

    val_preds = model.predict(X_val)
    mae = mean_absolute_error(y_val, val_preds)
    return model, mae


def run_lgbm(
    daily: pd.DataFrame,
    horizon_days: int = 90,
) -> pd.DataFrame:
    """
    Train LightGBM on historical daily spend and forecast recursively.

    Returns DataFrame with columns:
        ds, yhat, is_forecast (bool), model_mae
    """
    if daily.empty or len(daily) < 30:
        logger.warning("Not enough data for LightGBM (need ≥30 days, got %d)", len(daily))
        return pd.DataFrame(columns=["ds", "yhat", "is_forecast", "model_mae"])

    logger.info("Fitting LightGBM on %d days, forecasting %d days ahead", len(daily), horizon_days)

    val_size = min(30, len(daily) // 5)
    model, mae = _train_eval(daily.copy(), val_size=val_size)

    logger.info("LightGBM MAE on validation: %.2f", mae)

    # ── Recursive forecast ────────────────────────────────────────────────────
    # Extend history with predicted values one day at a time
    hist = daily[["ds", "y"]].copy()
    hist["ds"] = pd.to_datetime(hist["ds"])

    last_date = hist["ds"].max()
    future_rows = []

    for i in range(1, horizon_days + 1):
        next_date = last_date + pd.Timedelta(days=i)
        extended  = pd.concat([hist, pd.DataFrame(future_rows)], ignore_index=True)
        extended  = add_lgbm_features(extended)
        last_row  = extended.iloc[[-1]][LGBM_FEATURE_COLS].values
        pred      = float(np.clip(model.predict(last_row)[0], 0, None))
        future_rows.append({"ds": next_date, "y": pred})

    # Build result
    historical = hist.rename(columns={"y": "yhat"})
    historical["is_forecast"] = False
    historical["model_mae"]   = mae

    forecast_df = pd.DataFrame(future_rows).rename(columns={"y": "yhat"})
    forecast_df["is_forecast"] = True
    forecast_df["model_mae"]   = mae

    result = pd.concat([historical, forecast_df], ignore_index=True)
    result["yhat"] = result["yhat"].clip(lower=0)

    logger.info("LightGBM complete — %d historical + %d forecast rows", len(historical), len(forecast_df))
    return result
