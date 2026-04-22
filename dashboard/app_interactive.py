"""
Interactive Streamlit Dashboard with Data Source Selection
Complete version with all visualizations
"""
import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import tempfile
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import load_data
from src.features import build_feature_matrix
from src.models import run_anomaly_detection
from src.nlp import run_nlp_analysis
from src.risk_score import compute_risk_scores
from src.explainer import get_shap_values, get_global_importance

# Page config
st.set_page_config(
    page_title="Procurement Anomaly Detection",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern dark theme
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global font */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main background - gradient bluish black */
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
        color: #e2e8f0;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
    }
    
    /* Top Navbar */
    .top-navbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 60px;
        background: rgba(15, 23, 42, 0.95);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid #334155;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 2rem;
        z-index: 999;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    .navbar-brand {
        font-size: 1.2rem;
        font-weight: 700;
        color: #f1f5f9;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .navbar-links {
        display: flex;
        gap: 1rem;
        align-items: center;
    }
    
    .navbar-link {
        color: #cbd5e1;
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .navbar-link:hover {
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
    }
    
    .navbar-button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 0.5rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.3s;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .navbar-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }
    
    /* Add padding to main content to account for fixed navbar */
    .main .block-container {
        padding-top: 80px;
    }
    
    /* Footer */
    .footer {
        margin-top: 5rem;
        padding: 3rem 0 2rem 0;
        border-top: 1px solid #334155;
        background: rgba(15, 23, 42, 0.5);
    }
    
    .footer-content {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    .footer-section h4 {
        color: #f1f5f9;
        font-size: 1.1rem;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .footer-section p, .footer-section a {
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.8;
        text-decoration: none;
        display: block;
        margin-bottom: 0.5rem;
    }
    
    .footer-section a:hover {
        color: #a5b4fc;
    }
    
    .footer-bottom {
        text-align: center;
        padding-top: 2rem;
        border-top: 1px solid #334155;
        color: #64748b;
        font-size: 0.85rem;
    }
    
    .social-links {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }
    
    .social-link {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: rgba(99, 102, 241, 0.2);
        color: #a5b4fc;
        text-decoration: none;
        transition: all 0.3s;
    }
    
    .social-link:hover {
        background: rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }
    
    /* Sidebar - purple gradient with better styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    /* Sidebar header styling */
    [data-testid="stSidebar"] h1 {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        margin-bottom: 1.5rem !important;
        padding-bottom: 1rem !important;
        border-bottom: 2px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Sidebar section dividers */
    [data-testid="stSidebar"] hr {
        border: none;
        height: 1px;
        background: rgba(255, 255, 255, 0.2);
        margin: 1.5rem 0;
    }
    
    /* Headers */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #a5b4fc;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .sub-header {
        color: #94a3b8;
        margin-bottom: 2rem;
        font-size: 1.1rem;
        text-align: center;
        font-weight: 500;
    }
    
    /* All text in main area - light colors for dark background */
    .main .block-container {
        color: #e2e8f0;
    }
    
    .main p, .main span, .main div, .main label {
        color: #e2e8f0 !important;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #f1f5f9 !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        font-weight: 600;
        color: #cbd5e1 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.9rem;
        color: #94a3b8 !important;
    }
    
    /* Section headers */
    h1, h2, h3, h4, h5, h6 {
        color: #f1f5f9 !important;
        font-weight: 700;
    }
    
    .stMarkdown h2 {
        color: #f1f5f9 !important;
        font-weight: 700;
        margin-top: 1rem;
        font-size: 1.5rem;
    }
    
    .stMarkdown h3 {
        color: #e2e8f0 !important;
        font-weight: 600;
        font-size: 1.2rem;
    }
    
    /* Caption text */
    .stCaption, [data-testid="stCaptionContainer"], .stCaption * {
        color: #94a3b8 !important;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Info boxes */
    .stAlert {
        background: #1e293b;
        border-left: 4px solid #6366f1;
        border-radius: 8px;
        color: #e2e8f0 !important;
    }
    
    .stAlert p, .stAlert * {
        color: #e2e8f0 !important;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white !important;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 6px rgba(99, 102, 241, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(99, 102, 241, 0.4);
    }
    
    /* Selectbox - make dropdown visible */
    .stSelectbox label {
        color: #f1f5f9 !important;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .stSelectbox div[data-baseweb="select"] {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid #475569 !important;
    }
    
    .stSelectbox div[data-baseweb="select"] > div {
        background: transparent !important;
        color: #e2e8f0 !important;
    }
    
    .stSelectbox [data-baseweb="select"] span {
        color: #e2e8f0 !important;
    }
    
    /* Dropdown menu */
    [data-baseweb="popover"] {
        background: #1e293b !important;
    }
    
    [role="listbox"] {
        background: #1e293b !important;
        border: 1px solid #475569 !important;
    }
    
    [role="option"] {
        background: #1e293b !important;
        color: #e2e8f0 !important;
    }
    
    [role="option"]:hover {
        background: #334155 !important;
    }
    
    /* Text input - make visible */
    .stTextInput label {
        color: #f1f5f9 !important;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .stTextInput input {
        color: #f1f5f9 !important;
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid #475569 !important;
    }
    
    .stTextInput input::placeholder {
        color: #64748b !important;
    }
    
    /* Number input - make visible */
    .stNumberInput label {
        color: #f1f5f9 !important;
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    .stNumberInput input {
        color: #f1f5f9 !important;
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid #475569 !important;
    }
    
    /* Dataframe - make content visible */
    [data-testid="stDataFrame"] {
        background: rgba(30, 41, 59, 0.6) !important;
        border-radius: 12px;
        border: 1px solid #475569;
    }
    
    [data-testid="stDataFrame"] table {
        background: transparent !important;
    }
    
    [data-testid="stDataFrame"] thead {
        background: rgba(51, 65, 85, 0.8) !important;
    }
    
    [data-testid="stDataFrame"] thead th {
        color: #f1f5f9 !important;
        font-weight: 600 !important;
        background: rgba(51, 65, 85, 0.8) !important;
        border-bottom: 2px solid #6366f1 !important;
    }
    
    [data-testid="stDataFrame"] tbody tr {
        background: rgba(15, 23, 42, 0.4) !important;
        border-bottom: 1px solid #334155 !important;
    }
    
    [data-testid="stDataFrame"] tbody tr:hover {
        background: rgba(51, 65, 85, 0.6) !important;
    }
    
    [data-testid="stDataFrame"] tbody td {
        color: #e2e8f0 !important;
        background: transparent !important;
        padding: 0.75rem !important;
    }
    
    /* Dataframe scrollbar */
    [data-testid="stDataFrame"] ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    [data-testid="stDataFrame"] ::-webkit-scrollbar-track {
        background: #1e293b;
    }
    
    [data-testid="stDataFrame"] ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 4px;
    }
    
    [data-testid="stDataFrame"] ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #1e293b;
        border-radius: 12px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        background: transparent;
        color: #94a3b8 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white !important;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: #334155;
    }
    
    /* File uploader - make visible */
    [data-testid="stFileUploader"] {
        background: rgba(30, 41, 59, 0.6) !important;
        border-radius: 12px;
        padding: 1.5rem;
        border: 2px dashed #6366f1 !important;
    }
    
    [data-testid="stFileUploader"] label {
        color: #f1f5f9 !important;
        font-weight: 600;
    }
    
    [data-testid="stFileUploader"] * {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: #064e3b !important;
        border-left: 4px solid #10b981;
        color: #d1fae5 !important;
    }
    
    .stSuccess * {
        color: #d1fae5 !important;
    }
    
    .stError {
        background: #7f1d1d !important;
        border-left: 4px solid #ef4444;
        color: #fecaca !important;
    }
    
    .stError * {
        color: #fecaca !important;
    }
    
    .stWarning {
        background: #78350f !important;
        border-left: 4px solid #f59e0b;
        color: #fde68a !important;
    }
    
    .stWarning * {
        color: #fde68a !important;
    }
    
    .stInfo {
        background: #1e3a8a !important;
        border-left: 4px solid #3b82f6;
        color: #bfdbfe !important;
    }
    
    .stInfo * {
        color: #bfdbfe !important;
    }
    
    /* Markdown text */
    .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    .stMarkdown p, .stMarkdown li, .stMarkdown span {
        color: #e2e8f0 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #1e293b;
        color: #e2e8f0 !important;
        border-radius: 8px;
    }
    
    /* Column config */
    [data-testid="column"] {
        background: transparent;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #6366f1 !important;
    }
</style>
""", unsafe_allow_html=True)

# Top Navbar
st.markdown("""
<div class="top-navbar">
    <div class="navbar-brand">
        <span>🔍</span>
        <span>Procurement Anomaly Detection</span>
    </div>
    <div class="navbar-links">
        <a href="https://github.com/ayushv-nitj/public-procurement-anomaly-detection" target="_blank" class="navbar-link">
            <span>📂</span>
            <span>GitHub</span>
        </a>
        <a href="?page=about" class="navbar-button" onclick="window.location.search='?page=about'">
            <span>👥</span>
            <span>About Us</span>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# Check if we should show About page
query_params = st.query_params
if query_params.get("page") == "about":
    # Redirect to About page
    st.switch_page("pages/about.py")

# Header
st.markdown('<h1 class="main-header">🔍 Public Procurement Anomaly Detection</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-powered detection of suspicious patterns in government contracts</p>', unsafe_allow_html=True)

# Sidebar - Data Source Selection with better styling
st.sidebar.markdown("### 📊 Data Source")
st.sidebar.markdown("---")
source_type = st.sidebar.selectbox(
    "Select Data Source",
    ["Generate Synthetic", "Upload CSV", "Upload JSON", "Upload XML", "Fetch from API"]
)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None

# Data input based on source
df = None
error_message = None

try:
    if source_type == "Generate Synthetic":
        st.sidebar.markdown("---")
        st.sidebar.info("💡 Generates 500 realistic contracts with anomalies. Data will be different each time!")
        if st.sidebar.button("🎲 Generate & Analyze", use_container_width=True):
            with st.spinner("Generating synthetic data..."):
                df, validation_report = load_data(source='synthetic', validate=True)
                st.sidebar.success(f"✅ Generated {len(df)} contracts")
                
                # Show validation info
                if validation_report:
                    st.sidebar.info(f"📊 Quality Score: {validation_report['data_quality_score']:.0f}/100")
    
    elif source_type == "Upload CSV":
        st.sidebar.markdown("---")
        uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=['csv'])
        if uploaded_file:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            try:
                df, validation_report = load_data(source='csv', filepath=tmp_path, validate=True)
                st.sidebar.success(f"✅ Loaded {len(df)} contracts")
                if validation_report:
                    st.sidebar.info(f"📊 Quality Score: {validation_report['data_quality_score']:.0f}/100")
            finally:
                os.unlink(tmp_path)
    
    elif source_type == "Upload JSON":
        st.sidebar.markdown("---")
        uploaded_file = st.sidebar.file_uploader("Upload JSON file", type=['json'])
        if uploaded_file:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.json', delete=False) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            try:
                df, validation_report = load_data(source='json', filepath=tmp_path, validate=True)
                st.sidebar.success(f"✅ Loaded {len(df)} contracts")
                if validation_report:
                    st.sidebar.info(f"📊 Quality Score: {validation_report['data_quality_score']:.0f}/100")
            finally:
                os.unlink(tmp_path)
    
    elif source_type == "Upload XML":
        st.sidebar.markdown("---")
        uploaded_file = st.sidebar.file_uploader("Upload XML file", type=['xml'])
        if uploaded_file:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.xml', delete=False) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            try:
                df, validation_report = load_data(source='xml', filepath=tmp_path, validate=True)
                st.sidebar.success(f"✅ Loaded {len(df)} contracts")
                if validation_report:
                    st.sidebar.info(f"📊 Quality Score: {validation_report['data_quality_score']:.0f}/100")
            finally:
                os.unlink(tmp_path)
    
    elif source_type == "Fetch from API":
        st.sidebar.markdown("---")
        st.sidebar.warning("⚠️ Requires valid API credentials")
        api_url = st.sidebar.text_input("API URL", placeholder="https://api.data.gov.in/resource/...")
        api_key = st.sidebar.text_input("API Key (optional)", type="password")
        api_format = st.sidebar.selectbox("Format", ["json", "xml", "csv"])
        api_limit = st.sidebar.number_input("Limit", min_value=10, max_value=500, value=100)
        
        if st.sidebar.button("🌐 Fetch & Analyze", use_container_width=True):
            if not api_url:
                st.sidebar.error("❌ API URL is required")
            else:
                with st.spinner("Fetching data from API..."):
                    params = {'format': api_format, 'limit': api_limit}
                    df, validation_report = load_data(
                        source='api',
                        api_url=api_url,
                        api_key=api_key if api_key else None,
                        params=params,
                        validate=True
                    )
                    st.sidebar.success(f"✅ Fetched {len(df)} contracts")
                    if validation_report:
                        st.sidebar.info(f"📊 Quality Score: {validation_report['data_quality_score']:.0f}/100")

except Exception as e:
    error_message = str(e)
    st.sidebar.error(f"❌ Error: {error_message}")

# Sidebar footer info
st.sidebar.markdown("---")
st.sidebar.markdown("""
### ℹ️ About

**Procurement Anomaly Detection**

AI-powered system for detecting suspicious patterns in government contracts.

**Team:**
- 👨‍💻 Ayush Verma (Leader)
- 👨‍💼 Ishaan Rai
- 👨‍🔬 Priyanshu Raj
- 👨‍🎨 Aditya Prakash

[📂 GitHub](https://github.com/ayushv-nitj/public-procurement-anomaly-detection) | [👥 About Us](?page=about)
""")

# Process data if loaded
if df is not None:
    with st.spinner("Running anomaly detection pipeline..."):
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
        explainer_obj, shap_values = get_shap_values(if_model, feature_matrix, feature_names)
        importance = get_global_importance(shap_values, feature_names)
        
        # Store in session state
        st.session_state.results = {
            'df': df,
            'feature_names': feature_names,
            'shap_values': shap_values,
            'importance': importance,
            'similar_pairs': similar_pairs
        }

# Display results
if st.session_state.results:
    results = st.session_state.results
    df = results['df']
    
    # Summary metrics in colored cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Contracts",
            len(df),
            delta=None
        )
    with col2:
        anomaly_rate = (df["is_anomaly"].sum() / len(df) * 100)
        st.metric(
            "Anomalies Detected",
            int(df["is_anomaly"].sum()),
            delta=f"{anomaly_rate:.1f}%",
            delta_color="inverse"
        )
    with col3:
        st.metric(
            "High Risk",
            int((df["risk_label"] == "High").sum())
        )
    with col4:
        st.metric(
            "Avg Risk Score",
            f"{df['risk_score'].mean():.1f}"
        )
    
    st.markdown("---")
    
    # Main visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk Score Distribution
        st.subheader("📊 Risk Score Distribution")
        
        # Create histogram with color coding
        fig = go.Figure()
        
        # Low risk (0-70)
        low_risk = df[df['risk_score'] < 70]
        fig.add_trace(go.Histogram(
            x=low_risk['risk_score'],
            name='Low',
            marker_color='#4ade80',
            xbins=dict(start=0, end=100, size=5)
        ))
        
        # High risk (70-100)
        high_risk = df[df['risk_score'] >= 70]
        fig.add_trace(go.Histogram(
            x=high_risk['risk_score'],
            name='High',
            marker_color='#ef4444',
            xbins=dict(start=0, end=100, size=5)
        ))
        
        fig.update_layout(
            title="Distribution of Risk Scores",
            xaxis_title="risk_score",
            yaxis_title="Count",
            barmode='stack',
            template='plotly_dark',
            height=400,
            paper_bgcolor='#1e293b',
            plot_bgcolor='#0f172a',
            font=dict(color='#e2e8f0', size=12),
            title_font=dict(size=16, color='#f1f5f9', family='Inter')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Anomalies by Department
        st.subheader("🏛️ Anomalies by Department")
        
        dept_stats = df.groupby("dept")["is_anomaly"].sum().sort_values(ascending=True)
        
        fig = go.Figure(go.Bar(
            x=dept_stats.values,
            y=dept_stats.index,
            orientation='h',
            marker=dict(
                color=dept_stats.values,
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Anomalies")
            )
        ))
        
        fig.update_layout(
            title="Anomalies by Department",
            xaxis_title="Anomalies",
            yaxis_title="Department",
            template='plotly_dark',
            height=400,
            paper_bgcolor='#1e293b',
            plot_bgcolor='#0f172a',
            font=dict(color='#e2e8f0', size=12),
            title_font=dict(size=16, color='#f1f5f9', family='Inter')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Flagged Contracts Table
    st.subheader("🚨 Flagged Contracts")
    st.caption("Filter by Risk Level")
    
    risk_filter = st.selectbox("", ["All", "High", "Low"], label_visibility="collapsed")
    
    # Apply filter
    if risk_filter == "All":
        filtered_df = df
    else:
        filtered_df = df[df["risk_label"] == risk_filter]
    
    # Display table
    display_df = filtered_df[["contract_id", "vendor_name", "dept", "amount", "award_date", "risk_score", "risk_label", "is_anomaly"]].copy()
    display_df = display_df.sort_values("risk_score", ascending=False)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=300,
        column_config={
            "amount": st.column_config.NumberColumn(
                "Amount",
                format="₹%.2f"
            ),
            "risk_score": st.column_config.NumberColumn(
                "Risk Score",
                format="%.2f"
            )
        }
    )
    
    st.markdown("---")
    
    # SHAP Feature Importance
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🧠 SHAP Feature Importance")
        st.caption("Global Feature Importance")
        
        importance_df = pd.DataFrame(results['importance'], columns=["Feature", "Importance"])
        
        fig = go.Figure(go.Bar(
            x=importance_df["Importance"],
            y=importance_df["Feature"],
            orientation='h',
            marker=dict(
                color=importance_df["Importance"],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Mean |SHAP|")
            )
        ))
        
        fig.update_layout(
            title="Global Feature Importance",
            xaxis_title="Mean |SHAP|",
            yaxis_title="Features",
            template='plotly_dark',
            height=400,
            paper_bgcolor='#1e293b',
            plot_bgcolor='#0f172a',
            font=dict(color='#e2e8f0', size=12),
            title_font=dict(size=16, color='#f1f5f9', family='Inter')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🔍 Per-Contract Explanation")
        st.caption("Select a flagged contract")
        
        # Select contract
        flagged_contracts = df[df["is_anomaly"] == 1]["contract_id"].tolist()
        
        if flagged_contracts:
            selected_contract = st.selectbox(
                "Select a flagged contract",
                flagged_contracts,
                label_visibility="collapsed"
            )
            
            if selected_contract:
                idx = df[df["contract_id"] == selected_contract].index[0]
                
                # SHAP values for this contract
                shap_vals = results['shap_values'][idx]
                feature_names = results['feature_names']
                
                shap_df = pd.DataFrame({
                    'Feature': feature_names,
                    'shap_value': shap_vals
                }).sort_values('shap_value', key=abs, ascending=False)
                
                fig = go.Figure(go.Bar(
                    x=shap_df['shap_value'],
                    y=shap_df['Feature'],
                    orientation='h',
                    marker=dict(
                        color=shap_df['shap_value'],
                        colorscale='RdBu',
                        cmid=0,
                        showscale=True,
                        colorbar=dict(title="shap_value")
                    )
                ))
                
                fig.update_layout(
                    title=f"SHAP values for {selected_contract}",
                    xaxis_title="shap_value",
                    yaxis_title="Features",
                    template='plotly_dark',
                    height=400,
                    paper_bgcolor='#1e293b',
                    plot_bgcolor='#0f172a',
                    font=dict(color='#e2e8f0', size=12),
                    title_font=dict(size=16, color='#f1f5f9', family='Inter')
                )
                
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No flagged contracts in this dataset")
    
    st.markdown("---")
    
    # Suspiciously Similar Descriptions
    st.subheader("📄 Suspiciously Similar Descriptions")
    
    if len(results['similar_pairs']) > 0:
        similar_data = []
        for a, b, sim in results['similar_pairs'][:10]:  # Top 10
            contract_a = df[df.index == a].iloc[0]
            contract_b = df[df.index == b].iloc[0]
            similar_data.append({
                'Contract A': contract_a['contract_id'],
                'Contract B': contract_b['contract_id'],
                'Similarity': f"{sim:.2%}",
                'Description A': contract_a['description'][:80] + "...",
                'Description B': contract_b['description'][:80] + "..."
            })
        
        similar_df = pd.DataFrame(similar_data)
        st.dataframe(similar_df, use_container_width=True, height=300)
    else:
        st.info("No suspiciously similar descriptions found")
    
    st.markdown("---")
    
    # Contract Amount vs Risk Score Scatter
    st.subheader("💰 Contract Amount vs Risk Score")
    
    fig = go.Figure()
    
    # Low risk points
    low_risk = df[df['risk_label'] == 'Low']
    fig.add_trace(go.Scatter(
        x=low_risk['amount'],
        y=low_risk['risk_score'],
        mode='markers',
        name='Low',
        marker=dict(
            color='#4ade80',
            size=8,
            opacity=0.6
        ),
        text=low_risk.apply(lambda row: f"ID: {row['contract_id']}<br>Vendor: {row['vendor_name']}<br>Dept: {row['dept']}", axis=1),
        hovertemplate='<b>%{text}</b><br>Amount: ₹%{x:,.0f}<br>Risk Score: %{y:.1f}<extra></extra>'
    ))
    
    # High risk points
    high_risk = df[df['risk_label'] == 'High']
    fig.add_trace(go.Scatter(
        x=high_risk['amount'],
        y=high_risk['risk_score'],
        mode='markers',
        name='High',
        marker=dict(
            color='#ef4444',
            size=10,
            opacity=0.8
        ),
        text=high_risk.apply(lambda row: f"ID: {row['contract_id']}<br>Vendor: {row['vendor_name']}<br>Dept: {row['dept']}", axis=1),
        hovertemplate='<b>%{text}</b><br>Amount: ₹%{x:,.0f}<br>Risk Score: %{y:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Contract Amount vs Risk Score",
        xaxis_title="Contract Amount (₹, log scale)",
        yaxis_title="risk_score",
        xaxis_type="log",
        template='plotly_dark',
        height=500,
        showlegend=True,
        legend=dict(title="risk_label"),
        paper_bgcolor='#1e293b',
        plot_bgcolor='#0f172a',
        font=dict(color='#e2e8f0', size=12),
        title_font=dict(size=16, color='#f1f5f9', family='Inter')
    )
    
    st.plotly_chart(fig, use_container_width=True)

else:
    # Welcome message
    st.info("👈 Select a data source from the sidebar to begin analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🚀 How to Use
        
        1. **Select a data source** from the sidebar
        2. **Upload your data** or generate synthetic data
        3. **Click the analyze button** to run the ML pipeline
        4. **Explore the results** in the interactive dashboard
        
        ### 📊 Supported Data Sources
        
        - 🎲 **Synthetic**: Generate realistic fake data (500 contracts)
        - 📄 **CSV**: Upload comma-separated values file
        - 📋 **JSON**: Upload JSON format file
        - 📝 **XML**: Upload XML format file
        - 🌐 **API**: Fetch from government data portals (requires credentials)
        """)
    
    with col2:
        st.markdown("""
        ### ✨ Features
        
        - ✅ Multi-source data loading
        - ✅ Ensemble anomaly detection (Isolation Forest + One-Class SVM)
        - ✅ NLP similarity analysis
        - ✅ Risk score calculation
        - ✅ SHAP explainability
        - ✅ Interactive visualizations
        - ✅ Dark theme UI
        - ✅ Real-time processing
        
        ### 📈 Visualizations
        
        - Risk score distribution
        - Anomalies by department
        - Feature importance (SHAP)
        - Per-contract explanations
        - Similar descriptions detection
        - Amount vs risk scatter plot
        """)

# Footer - Simplified version
st.markdown("---")
st.markdown("### 📧 Contact & Links")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    **🔍 About**
    
    AI-powered anomaly detection system
    
    **Team Leader:** Ayush Verma
    
    **Members:** Ishaan Rai, Priyanshu Raj, Aditya Prakash
    """)

with col2:
    st.markdown("""
    **🔗 Quick Links**
    
    [📂 GitHub](https://github.com/ayushv-nitj/public-procurement-anomaly-detection)
    
    [📖 Documentation](https://github.com/ayushv-nitj/public-procurement-anomaly-detection#readme)
    
    [👥 About Us](?page=about)
    """)

with col3:
    st.markdown("""
    **🛠️ Tech Stack**
    
    • Python, Scikit-learn, SHAP
    
    • Streamlit, Flask, Plotly
    
    • Pandas, NumPy, TF-IDF
    """)

with col4:
    st.markdown("""
    **📧 Contact**
    
    Professional Lab Project
    
    NIT Jamshedpur
    
    [GitHub Profile](https://github.com/ayushv-nitj)
    """)

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #64748b; font-size: 0.85rem;'>"
    "© 2026 Procurement Anomaly Detection System | Developed with ❤️ by Team Ayush Verma"
    "</p>",
    unsafe_allow_html=True
)
