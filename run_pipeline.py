"""
Run the full ML pipeline and export results for the frontend.
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from src.features import build_feature_matrix
from src.models import run_anomaly_detection
from src.nlp import run_nlp_analysis
from src.risk_score import compute_risk_scores
from src.explainer import get_shap_values, get_top_features, get_global_importance

def main():
    # Load data
    df = pd.read_csv("data/contracts.csv")
    print(f"Loaded {len(df)} contracts")

    # Feature engineering
    df, feature_matrix, feature_names, scaler = build_feature_matrix(df)
    print(f"Features: {feature_names}")

    # Anomaly detection
    if_model, ensemble_labels, ensemble_scores, model_results = run_anomaly_detection(feature_matrix)

    # NLP analysis
    nlp_scores, similar_pairs, vectorizer = run_nlp_analysis(df["description"].tolist())

    # Risk scores
    risk_scores, risk_labels = compute_risk_scores(
        ensemble_scores, nlp_scores, df["vendor_freq"].values
    )

    df["is_anomaly"] = ensemble_labels
    df["anomaly_score"] = ensemble_scores
    df["nlp_similarity"] = nlp_scores
    df["risk_score"] = risk_scores
    df["risk_label"] = risk_labels

    # SHAP
    explainer_obj, shap_values = get_shap_values(if_model, feature_matrix, feature_names)
    print("SHAP values computed")

    # Export for frontend
    os.makedirs("frontend", exist_ok=True)

    export_df = df[["contract_id", "vendor_name", "dept", "amount", "award_date",
                     "description", "is_anomaly", "risk_score", "risk_label",
                     "anomaly_score", "nlp_similarity", "vendor_freq"]].copy()

    importance = get_global_importance(shap_values, feature_names)

    dept_stats = df.groupby("dept").agg(
        total_contracts=("contract_id", "count"),
        anomalies=("is_anomaly", "sum"),
        avg_risk=("risk_score", "mean"),
        total_amount=("amount", "sum")
    ).reset_index().to_dict(orient="records")

    vendor_stats = df.groupby("vendor_name").agg(
        contracts=("contract_id", "count"),
        anomalies=("is_anomaly", "sum"),
        avg_risk=("risk_score", "mean"),
        total_amount=("amount", "sum")
    ).reset_index().sort_values("avg_risk", ascending=False).head(15).to_dict(orient="records")

    export_data = {
        "summary": {
            "total_contracts": int(len(df)),
            "total_anomalies": int(df["is_anomaly"].sum()),
            "high_risk_count": int((df["risk_label"] == "High").sum()),
            "avg_risk_score": round(float(df["risk_score"].mean()), 2),
            "max_risk_score": round(float(df["risk_score"].max()), 2),
            "total_amount": round(float(df["amount"].sum()), 2),
            "anomaly_rate": round(float(df["is_anomaly"].mean() * 100), 2)
        },
        "contracts": json.loads(export_df.to_json(orient="records")),
        "feature_importance": [
            {"feature": f, "importance": round(float(v), 4)} for f, v in importance
        ],
        "department_stats": dept_stats,
        "top_risky_vendors": vendor_stats,
        "similar_pairs": [
            {"contract_a": int(a), "contract_b": int(b), "similarity": float(s)}
            for a, b, s in similar_pairs
        ],
        "risk_distribution": {
            "bins": list(range(0, 105, 5)),
            "counts": [
                int(((df["risk_score"] >= lo) & (df["risk_score"] < lo + 5)).sum())
                for lo in range(0, 100, 5)
            ]
        }
    }

    with open("frontend/results.json", "w") as f:
        json.dump(export_data, f, indent=2)

    anomaly_count = int(df["is_anomaly"].sum())
    high_risk_count = int((df["risk_label"] == "High").sum())
    print(f"Exported frontend/results.json")
    print(f"Anomalies: {anomaly_count}, High Risk: {high_risk_count}")
    print("DONE - Pipeline complete!")


if __name__ == "__main__":
    main()
