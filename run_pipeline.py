"""
Run the full ML pipeline and export results for the frontend.
Supports multiple data sources: synthetic, API, CSV, XML, JSON
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from src.data_loader import load_data
from src.features import build_feature_matrix
from src.models import run_anomaly_detection
from src.nlp import run_nlp_analysis
from src.risk_score import compute_risk_scores
from src.explainer import get_shap_values, get_top_features, get_global_importance

def main(data_source='csv', **source_kwargs):
    """
    Run the ML pipeline with configurable data source.
    
    Args:
        data_source: 'synthetic', 'csv', 'json', 'xml', or 'api'
        **source_kwargs: Source-specific parameters
    
    Examples:
        main('synthetic')
        main('csv', filepath='data/contracts.csv')
        main('json', filepath='data/contracts.json')
        main('xml', filepath='data/contracts.xml')
        main('api', api_url='https://...', api_key='...', params={'format': 'json'})
    """
    # Load data from specified source (with validation)
    df, validation_report = load_data(source=data_source, validate=True, **source_kwargs)
    
    # Print validation summary
    if validation_report:
        print(f"\n{'='*60}")
        print("DATA VALIDATION SUMMARY")
        print(f"{'='*60}")
        print(f"Original rows: {validation_report['original_rows']}")
        print(f"Final rows: {validation_report['final_rows']}")
        print(f"Rows dropped: {validation_report['rows_dropped']}")
        print(f"Data quality score: {validation_report['data_quality_score']:.2f}/100")
        
        if validation_report.get('vendor_normalization'):
            vn = validation_report['vendor_normalization']
            print(f"Vendor normalization: {vn['unique_before']} → {vn['unique_after']} "
                  f"({vn['reduction']} merged)")
        
        print(f"{'='*60}\n")

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
    import argparse
    
    parser = argparse.ArgumentParser(description='Run procurement anomaly detection pipeline')
    parser.add_argument('--source', type=str, default='csv', 
                       choices=['synthetic', 'csv', 'json', 'xml', 'api'],
                       help='Data source type')
    parser.add_argument('--filepath', type=str, help='Path to data file (for csv/json/xml)')
    parser.add_argument('--api-url', type=str, help='API endpoint URL')
    parser.add_argument('--api-key', type=str, help='API key for authentication')
    parser.add_argument('--format', type=str, help='API response format (json/xml/csv)')
    parser.add_argument('--offset', type=int, default=0, help='API pagination offset')
    parser.add_argument('--limit', type=int, default=100, help='API pagination limit')
    
    args = parser.parse_args()
    
    # Build kwargs based on source type
    kwargs = {}
    
    if args.source in ['csv', 'json', 'xml']:
        if args.filepath:
            kwargs['filepath'] = args.filepath
        elif args.source == 'csv':
            kwargs['filepath'] = 'data/contracts.csv'  # default
    
    elif args.source == 'api':
        if not args.api_url:
            print("Error: --api-url is required for API source")
            exit(1)
        kwargs['api_url'] = args.api_url
        if args.api_key:
            kwargs['api_key'] = args.api_key
        
        # Build API params
        params = {}
        if args.format:
            params['format'] = args.format
        if args.offset:
            params['offset'] = args.offset
        if args.limit:
            params['limit'] = args.limit
        if params:
            kwargs['params'] = params
    
    main(data_source=args.source, **kwargs)
