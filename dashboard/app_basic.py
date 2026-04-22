"""
Streamlit Dashboard — Public Procurement Anomaly Detection
Main entry point: streamlit run dashboard/app.py
"""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.features import build_feature_matrix
from src.models import run_anomaly_detection
from src.nlp import run_nlp_analysis
from src.risk_score import compute_risk_scores
from src.explainer import get_shap_values, get_top_features, get_global_importance

# --- Page Config ---
st.set_page_config(
    page_title="Procurement Anomaly Detection",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .main { padding: 1rem 2rem; }
    .stMetric { background: linear-gradient(135deg, #1e1e2e, #2d2d44);
                padding: 1rem; border-radius: 12px; border: 1px solid #3d3d5c; }
    h1 { color: #e0e0ff; }
    .risk-high { color: #ff4d6a; font-weight: bold; }
    .risk-low { color: #4dff88; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_and_process_data():
    """Load data and run full pipeline (cached)."""
    data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "data", "contracts.csv")
    if not os.path.exists(data_path):
        st.error("❌ Dataset not found! Run `python data/generate_data.py` first.")
        st.stop()

    df = pd.read_csv(data_path)

    # Feature engineering
    df, feature_matrix, feature_names, scaler = build_feature_matrix(df)

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
    explainer, shap_values = get_shap_values(if_model, feature_matrix, feature_names)

    # Export results for frontend
    export_for_frontend(df, shap_values, feature_names, similar_pairs)

    return df, shap_values, feature_names, similar_pairs, model_results


def export_for_frontend(df, shap_values, feature_names, similar_pairs):
    """Export results to JSON for the standalone frontend."""
    export_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
    os.makedirs(export_dir, exist_ok=True)

    # Contracts data
    export_df = df[["contract_id", "vendor_name", "dept", "amount", "award_date",
                     "description", "is_anomaly", "risk_score", "risk_label",
                     "anomaly_score", "nlp_similarity", "vendor_freq"]].copy()

    # Global feature importance
    importance = get_global_importance(shap_values, feature_names)

    # Department stats
    dept_stats = df.groupby("dept").agg(
        total_contracts=("contract_id", "count"),
        anomalies=("is_anomaly", "sum"),
        avg_risk=("risk_score", "mean"),
        total_amount=("amount", "sum")
    ).reset_index().to_dict(orient="records")

    # Top risky vendors
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
        "feature_importance": [{"feature": f, "importance": round(float(v), 4)} for f, v in importance],
        "department_stats": dept_stats,
        "top_risky_vendors": vendor_stats,
        "similar_pairs": [{"contract_a": int(a), "contract_b": int(b), "similarity": float(s)}
                          for a, b, s in similar_pairs],
        "risk_distribution": {
            "bins": list(range(0, 105, 5)),
            "counts": [int(((df["risk_score"] >= lo) & (df["risk_score"] < lo + 5)).sum())
                       for lo in range(0, 100, 5)]
        }
    }

    output_path = os.path.join(export_dir, "results.json")
    with open(output_path, "w") as f:
        json.dump(export_data, f, indent=2)


def main():
    st.title("🔍 Public Procurement Anomaly Detection")
    st.markdown("*AI-powered detection of suspicious patterns in government contracts*")

    df, shap_values, feature_names, similar_pairs, model_results = load_and_process_data()

    # --- KPI Cards ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Contracts", len(df))
    with col2:
        st.metric("Anomalies Detected", int(df["is_anomaly"].sum()),
                   delta=f"{df['is_anomaly'].mean()*100:.1f}%")
    with col3:
        st.metric("High Risk", int((df["risk_label"] == "High").sum()))
    with col4:
        st.metric("Avg Risk Score", f"{df['risk_score'].mean():.1f}")

    st.markdown("---")

    # --- Risk Distribution ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 Risk Score Distribution")
        fig_hist = px.histogram(df, x="risk_score", nbins=20,
                                color="risk_label",
                                color_discrete_map={"High": "#ff4d6a", "Low": "#4dff88"},
                                title="Distribution of Risk Scores")
        fig_hist.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_right:
        st.subheader("🏛️ Anomalies by Department")
        dept_anom = df.groupby("dept")["is_anomaly"].sum().reset_index()
        dept_anom.columns = ["Department", "Anomalies"]
        fig_dept = px.bar(dept_anom, x="Anomalies", y="Department", orientation="h",
                          color="Anomalies", color_continuous_scale="Reds")
        fig_dept.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_dept, use_container_width=True)

    st.markdown("---")

    # --- Anomaly Table ---
    st.subheader("🚨 Flagged Contracts")

    risk_filter = st.selectbox("Filter by Risk Level", ["All", "High", "Low"])
    if risk_filter != "All":
        filtered_df = df[df["risk_label"] == risk_filter]
    else:
        filtered_df = df

    display_cols = ["contract_id", "vendor_name", "dept", "amount",
                    "award_date", "risk_score", "risk_label", "is_anomaly"]
    st.dataframe(
        filtered_df[display_cols].sort_values("risk_score", ascending=False),
        use_container_width=True, height=400
    )

    st.markdown("---")

    # --- SHAP Explainer ---
    st.subheader("🧠 SHAP Feature Importance")

    col_shap1, col_shap2 = st.columns(2)

    with col_shap1:
        st.markdown("**Global Feature Importance**")
        importance = get_global_importance(shap_values, feature_names)
        imp_df = pd.DataFrame(importance, columns=["Feature", "Mean |SHAP|"])
        fig_imp = px.bar(imp_df, x="Mean |SHAP|", y="Feature", orientation="h",
                         color="Mean |SHAP|", color_continuous_scale="Viridis")
        fig_imp.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig_imp, use_container_width=True)

    with col_shap2:
        st.markdown("**Per-Contract Explanation**")
        anomaly_ids = df[df["is_anomaly"] == 1]["contract_id"].tolist()
        if anomaly_ids:
            selected = st.selectbox("Select a flagged contract", anomaly_ids)
            idx = df[df["contract_id"] == selected].index[0]
            top_feats = get_top_features(shap_values, feature_names, idx)
            feat_df = pd.DataFrame(top_feats)
            fig_feat = px.bar(feat_df, x="shap_value", y="feature", orientation="h",
                              color="shap_value", color_continuous_scale="RdBu_r",
                              title=f"SHAP values for {selected}")
            fig_feat.update_layout(template="plotly_dark", height=350)
            st.plotly_chart(fig_feat, use_container_width=True)

    st.markdown("---")

    # --- Similar Pairs ---
    if similar_pairs:
        st.subheader("📝 Suspiciously Similar Descriptions")
        pairs_data = []
        for i, j, score in similar_pairs[:20]:
            pairs_data.append({
                "Contract A": df.iloc[i]["contract_id"],
                "Contract B": df.iloc[j]["contract_id"],
                "Similarity": f"{score:.2%}",
                "Description A": df.iloc[i]["description"][:80] + "...",
                "Description B": df.iloc[j]["description"][:80] + "..."
            })
        st.dataframe(pd.DataFrame(pairs_data), use_container_width=True)

    # --- Amount scatter ---
    st.subheader("💰 Contract Amount vs Risk Score")
    fig_scatter = px.scatter(df, x="amount", y="risk_score",
                             color="risk_label",
                             color_discrete_map={"High": "#ff4d6a", "Low": "#4dff88"},
                             hover_data=["contract_id", "vendor_name", "dept"],
                             size="risk_score", size_max=12,
                             title="Contract Amount vs Risk Score")
    fig_scatter.update_layout(template="plotly_dark", height=500)
    fig_scatter.update_xaxes(type="log", title="Contract Amount (₹, log scale)")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")
    st.caption("Public Procurement Anomaly Detection System — BTech CS Project")


if __name__ == "__main__":
    main()
