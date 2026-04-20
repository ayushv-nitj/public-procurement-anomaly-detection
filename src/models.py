"""
Anomaly Detection Models
Isolation Forest + One-Class SVM ensemble for unsupervised anomaly detection.
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM


def train_isolation_forest(feature_matrix, contamination=0.1, random_state=42):
    """
    Train an Isolation Forest model.
    
    Returns:
        model: trained IsolationForest
        predictions: -1 for anomaly, 1 for normal
        scores: anomaly scores (lower = more anomalous)
    """
    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        max_samples="auto",
        random_state=random_state,
        n_jobs=-1
    )
    model.fit(feature_matrix)
    predictions = model.predict(feature_matrix)
    scores = model.decision_function(feature_matrix)
    
    return model, predictions, scores


def train_one_class_svm(feature_matrix, nu=0.1):
    """
    Train a One-Class SVM model.
    
    Returns:
        model: trained OneClassSVM
        predictions: -1 for anomaly, 1 for normal
        scores: decision function scores
    """
    model = OneClassSVM(
        kernel="rbf",
        gamma="scale",
        nu=nu
    )
    model.fit(feature_matrix)
    predictions = model.predict(feature_matrix)
    scores = model.decision_function(feature_matrix)
    
    return model, predictions, scores


def ensemble_predict(if_predictions, svm_predictions, if_scores, svm_scores):
    """
    Ensemble: flag as anomaly if EITHER model flags it.
    Also compute a combined anomaly score.
    
    Returns:
        ensemble_labels: 1 for anomaly, 0 for normal
        ensemble_scores: normalized combined score (0 to 1, higher = more anomalous)
    """
    # Convert sklearn convention (-1=anomaly) to (1=anomaly, 0=normal)
    if_anomaly = (if_predictions == -1).astype(int)
    svm_anomaly = (svm_predictions == -1).astype(int)
    
    # Union: anomaly if either flags it
    ensemble_labels = np.maximum(if_anomaly, svm_anomaly)
    
    # Combine scores: normalize each to [0, 1] range (inverted so higher = more anomalous)
    if_norm = 1 - (if_scores - if_scores.min()) / (if_scores.max() - if_scores.min() + 1e-8)
    svm_norm = 1 - (svm_scores - svm_scores.min()) / (svm_scores.max() - svm_scores.min() + 1e-8)
    
    # Weighted average (IF gets more weight as it's typically better for tabular data)
    ensemble_scores = 0.6 * if_norm + 0.4 * svm_norm
    
    return ensemble_labels, ensemble_scores


def run_anomaly_detection(feature_matrix):
    """
    Full anomaly detection pipeline.
    
    Returns:
        if_model: trained Isolation Forest (needed for SHAP)
        ensemble_labels: binary anomaly labels
        ensemble_scores: continuous anomaly scores
        results dict with all intermediate outputs
    """
    # Train both models
    if_model, if_preds, if_scores = train_isolation_forest(feature_matrix)
    svm_model, svm_preds, svm_scores = train_one_class_svm(feature_matrix)
    
    # Ensemble
    ensemble_labels, ensemble_scores = ensemble_predict(
        if_preds, svm_preds, if_scores, svm_scores
    )
    
    results = {
        "if_model": if_model,
        "svm_model": svm_model,
        "if_predictions": if_preds,
        "svm_predictions": svm_preds,
        "if_scores": if_scores,
        "svm_scores": svm_scores,
        "ensemble_labels": ensemble_labels,
        "ensemble_scores": ensemble_scores
    }
    
    print(f"Isolation Forest flagged: {sum(if_preds == -1)} anomalies")
    print(f"One-Class SVM flagged:    {sum(svm_preds == -1)} anomalies")
    print(f"Ensemble flagged:         {sum(ensemble_labels)} anomalies")
    
    return if_model, ensemble_labels, ensemble_scores, results
