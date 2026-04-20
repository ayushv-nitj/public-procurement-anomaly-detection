"""
Risk Score Fusion Module
Combines anomaly detection scores, NLP similarity, and vendor frequency
into a single normalized risk score (0-100).
"""

import numpy as np

WEIGHT_ANOMALY = 0.50
WEIGHT_NLP = 0.30
WEIGHT_VENDOR_FREQ = 0.20
HIGH_RISK_THRESHOLD = 70


def normalize_to_0_100(arr):
    arr = np.array(arr, dtype=float)
    min_val, max_val = arr.min(), arr.max()
    if max_val - min_val < 1e-8:
        return np.full_like(arr, 50.0)
    return (arr - min_val) / (max_val - min_val) * 100


def compute_risk_scores(anomaly_scores, nlp_scores, vendor_freq):
    anomaly_norm = normalize_to_0_100(anomaly_scores)
    nlp_norm = normalize_to_0_100(nlp_scores)
    vendor_norm = normalize_to_0_100(vendor_freq)

    risk_scores = (
        WEIGHT_ANOMALY * anomaly_norm +
        WEIGHT_NLP * nlp_norm +
        WEIGHT_VENDOR_FREQ * vendor_norm
    )
    risk_scores = np.clip(np.round(risk_scores, 2), 0, 100)
    risk_labels = np.where(risk_scores >= HIGH_RISK_THRESHOLD, "High", "Low")

    print(f"Risk Score: mean={risk_scores.mean():.2f}, max={risk_scores.max():.2f}, "
          f"high_risk={sum(risk_labels == 'High')}, low_risk={sum(risk_labels == 'Low')}")

    return risk_scores, risk_labels
