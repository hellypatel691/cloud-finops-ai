"""
Isolation Forest anomaly detection.
Wraps sklearn's IsolationForest with our feature pipeline.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.ml.features import engineer_features, get_feature_matrix


def run_isolation_forest(
    df: pd.DataFrame,
    contamination: float = 0.05,
    n_estimators: int = 100,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Fit Isolation Forest on the feature matrix.
    Adds columns: if_score (0→1, higher = more anomalous), if_anomaly (bool)
    """
    if df.empty or len(df) < 10:
        df["if_score"]   = 0.0
        df["if_anomaly"] = False
        return df

    df = engineer_features(df)
    X  = get_feature_matrix(df)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    clf = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=random_state,
        n_jobs=-1,
    )
    clf.fit(X_scaled)

    # decision_function: more negative = more anomalous
    raw_scores = clf.decision_function(X_scaled)

    # Flip and normalise to [0, 1]
    flipped = -raw_scores
    min_s, max_s = flipped.min(), flipped.max()
    if max_s > min_s:
        normalised = (flipped - min_s) / (max_s - min_s)
    else:
        normalised = np.zeros_like(flipped)

    df["if_score"]   = normalised
    df["if_anomaly"] = clf.predict(X_scaled) == -1   # -1 = anomaly in sklearn

    return df
