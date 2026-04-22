"""
Flask Backend API for Procurement Anomaly Detection
Handles data loading, processing, and returns results
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
import json
import tempfile
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import load_data
from src.features import build_feature_matrix
from src.models import run_anomaly_detection
from src.nlp import run_nlp_analysis
from src.risk_score import compute_risk_scores
from src.explainer import get_shap_values, get_global_importance

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Remove the index route - Flask should only serve API endpoints
# Frontend files are served by the Python HTTP server on port 8080

@app.route('/api/process', methods=['POST'])
def process_data():
    """
    Process data from various sources and return anomaly detection results
    
    Expected JSON payload:
    {
        "source": "csv|json|xml|synthetic|api",
        "data": "file content as string" (for csv/json/xml),
        "api_url": "..." (for api),
        "api_key": "..." (for api),
        "api_format": "json|xml|csv" (for api),
        "api_limit": 100 (for api)
    }
    """
    try:
        data = request.json
        source = data.get('source')
        
        if not source:
            return jsonify({'error': 'Source type is required'}), 400
        
        # Load data based on source
        if source == 'synthetic':
            df = load_data(source='synthetic')
            
        elif source in ['csv', 'json', 'xml']:
            file_content = data.get('data')
            if not file_content:
                return jsonify({'error': f'{source.upper()} data is required'}), 400
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{source}', delete=False) as tmp:
                tmp.write(file_content)
                tmp_path = tmp.name
            
            try:
                df = load_data(source=source, filepath=tmp_path)
            finally:
                os.unlink(tmp_path)
                
        elif source == 'api':
            api_url = data.get('api_url')
            api_key = data.get('api_key')
            api_format = data.get('api_format', 'json')
            api_limit = data.get('api_limit', 100)
            
            if not api_url:
                return jsonify({'error': 'API URL is required'}), 400
            
            params = {
                'format': api_format,
                'limit': api_limit
            }
            
            df = load_data(
                source='api',
                api_url=api_url,
                api_key=api_key,
                params=params
            )
        else:
            return jsonify({'error': f'Invalid source: {source}'}), 400
        
        # Run the ML pipeline
        df, feature_matrix, feature_names, scaler = build_feature_matrix(df)
        if_model, ensemble_labels, ensemble_scores, model_results = run_anomaly_detection(feature_matrix)
        nlp_scores, similar_pairs, vectorizer = run_nlp_analysis(df["description"].tolist())
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
        
        # Prepare response
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
        
        result = {
            "success": True,
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
        
        return jsonify(result)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error processing data: {error_trace}")
        return jsonify({
            'success': False,
            'error': str(e),
            'details': error_trace
        }), 500

@app.route('/api/sample-data/<source>')
def get_sample_data(source):
    """Get sample data for a given source"""
    try:
        if source == 'csv':
            with open('data/contracts.csv', 'r') as f:
                return f.read()[:5000]  # First 5000 chars as sample
        elif source == 'json':
            with open('data/sample_contracts.json', 'r') as f:
                return f.read()
        elif source == 'xml':
            with open('data/sample_contracts.xml', 'r') as f:
                return f.read()
        else:
            return jsonify({'error': 'Invalid source'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/save-results', methods=['POST'])
def save_results():
    """Save results to frontend/results.json for dashboard"""
    try:
        data = request.json
        
        # Save to frontend/results.json
        with open('frontend/results.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({'success': True, 'message': 'Results saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask API server...")
    print("API Endpoints: http://localhost:5000/api")
    print("Note: Frontend is served separately on port 8080")
    app.run(debug=True, port=5000)
