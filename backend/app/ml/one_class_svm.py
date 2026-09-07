"""
One-Class SVM anomaly detection.
Used as a second ML opinion alongside Isolation Forest.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

from app.ml.features import engineer_features, get_feature_matrix


def run_one_class_svm(
    df: pd.DataFrame,
    nu: float = 0.05,
    kernel: str = "rbf",
    gamma: str = "scale",
) -> pd.DataFrame:
    """
    Fit One-Class SVM on the feature matrix.
    Adds: svm_score (0→1), svm_anomaly (bool)

    Note: OC-SVM is slower than IF on large datasets.
    We subsample to 5000 rows for fitting and predict on all.
    """
    if df.empty or len(df) < 10:
        df["svm_score"]   = 0.0
        df["svm_anomaly"] = False
        return df

    df = engineer_features(df)
    X  = get_feature_matrix(df)

    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Subsample for training if large
    n_train = min(len(X_scaled), 5000)
    idx     = np.random.default_rng(42).choice(len(X_scaled), n_train, replace=False)
    X_train = X_scaled[idx]

    clf = OneClassSVM(nu=nu, kernel=kernel, gamma=gamma)
    clf.fit(X_train)

    raw = clf.decision_function(X_scaled)   # positive = normal, negative = anomaly
    flipped = -raw
    min_s, max_s = flipped.min(), flipped.max()
    if max_s > min_s:
        normalised = (flipped - min_s) / (max_s - min_s)
    else:
        normalised = np.zeros_like(flipped)

    df["svm_score"]   = normalised
    df["svm_anomaly"] = clf.predict(X_scaled) == -1

    return df
