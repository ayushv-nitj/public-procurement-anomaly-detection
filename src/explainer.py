"""
SHAP Explainability Wrapper
Generates feature importance explanations for anomaly predictions.
"""

import numpy as np
import shap


def get_shap_values(if_model, feature_matrix, feature_names):
    """
    Compute SHAP values for Isolation Forest predictions.
    Uses TreeExplainer for tree-based models.
    """
    explainer = shap.TreeExplainer(if_model)
    shap_values = explainer.shap_values(feature_matrix)
    return explainer, shap_values


def get_top_features(shap_values, feature_names, contract_idx, top_n=5):
    """Get top N most influential features for a specific contract."""
    vals = shap_values[contract_idx]
    abs_vals = np.abs(vals)
    top_indices = abs_vals.argsort()[-top_n:][::-1]

    top_features = []
    for idx in top_indices:
        top_features.append({
            "feature": feature_names[idx],
            "shap_value": round(float(vals[idx]), 4),
            "abs_importance": round(float(abs_vals[idx]), 4)
        })
    return top_features


def get_global_importance(shap_values, feature_names):
    """Get global feature importance (mean absolute SHAP values)."""
    mean_abs = np.abs(shap_values).mean(axis=0)
    importance = sorted(
        zip(feature_names, mean_abs),
        key=lambda x: x[1], reverse=True
    )
    return importance
