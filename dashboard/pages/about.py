"""
About Us Page
"""
import streamlit as st

st.set_page_config(
    page_title="About Us - Procurement Anomaly Detection",
    page_icon="👥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
        color: #e2e8f0;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
    }
    
    .team-header {
        text-align: center;
        padding: 3rem 0;
    }
    
    .team-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .team-subtitle {
        font-size: 1.2rem;
        color: #94a3b8;
        margin-bottom: 3rem;
    }
    
    .team-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid #475569;
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s;
        height: 100%;
    }
    
    .team-card:hover {
        transform: translateY(-5px);
        border-color: #6366f1;
        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
    }
    
    .team-role {
        display: inline-block;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .team-name {
        font-size: 1.5rem;
        font-weight: 700;
        color: #f1f5f9;
        margin: 1rem 0 0.5rem 0;
    }
    
    .team-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .project-info {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid #475569;
        border-radius: 16px;
        padding: 2rem;
        margin: 3rem 0;
    }
    
    .project-info h3 {
        color: #f1f5f9;
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }
    
    .project-info p {
        color: #cbd5e1;
        font-size: 1.1rem;
        line-height: 1.8;
    }
    
    .tech-stack {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-top: 2rem;
    }
    
    .tech-badge {
        background: rgba(99, 102, 241, 0.2);
        border: 1px solid #6366f1;
        color: #a5b4fc;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="team-header">
    <h1 class="team-title">👥 Our Team</h1>
    <p class="team-subtitle">Meet the minds behind the Procurement Anomaly Detection System</p>
</div>
""", unsafe_allow_html=True)

# Team Members
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="team-card">
        <div class="team-icon">👨‍💻</div>
        <div class="team-role">Team Leader</div>
        <h3 class="team-name">Ayush Verma</h3>
        <p style="color: #94a3b8; margin-top: 0.5rem;">Project Lead & ML Engineer</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="team-card">
        <div class="team-icon">👨‍💼</div>
        <div class="team-role">Team Member</div>
        <h3 class="team-name">Ishaan Rai</h3>
        <p style="color: #94a3b8; margin-top: 0.5rem;">Backend Developer</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="team-card">
        <div class="team-icon">👨‍🔬</div>
        <div class="team-role">Team Member</div>
        <h3 class="team-name">Priyanshu Raj</h3>
        <p style="color: #94a3b8; margin-top: 0.5rem;">Data Scientist</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="team-card">
        <div class="team-icon">👨‍🎨</div>
        <div class="team-role">Team Member</div>
        <h3 class="team-name">Aditya Prakash</h3>
        <p style="color: #94a3b8; margin-top: 0.5rem;">Frontend Developer</p>
    </div>
    """, unsafe_allow_html=True)

# Project Information
st.markdown("""
<div class="project-info">
    <h3>🔍 About the Project</h3>
    <p>
        The <strong>Procurement Anomaly Detection System</strong> is an AI-powered solution designed to identify 
        suspicious patterns in government procurement contracts. Using advanced machine learning techniques 
        including Isolation Forest, One-Class SVM, and NLP analysis, our system helps detect potential fraud, 
        corruption, and irregularities in public procurement processes.
    </p>
    <p style="margin-top: 1rem;">
        This project was developed as part of our professional lab coursework, combining cutting-edge 
        technology with real-world applications to promote transparency and accountability in government spending.
    </p>
</div>
""", unsafe_allow_html=True)

# Tech Stack
st.markdown("<h3 style='color: #f1f5f9; margin-top: 3rem; margin-bottom: 1.5rem;'>🛠️ Technology Stack</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid #475569; border-radius: 12px; padding: 1.5rem;">
        <h4 style="color: #f1f5f9; margin-bottom: 1rem;">🤖 Machine Learning</h4>
        <div class="tech-stack">
            <span class="tech-badge">Scikit-learn</span>
            <span class="tech-badge">SHAP</span>
            <span class="tech-badge">Pandas</span>
            <span class="tech-badge">NumPy</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid #475569; border-radius: 12px; padding: 1.5rem;">
        <h4 style="color: #f1f5f9; margin-bottom: 1rem;">🌐 Web Technologies</h4>
        <div class="tech-stack">
            <span class="tech-badge">Streamlit</span>
            <span class="tech-badge">Flask</span>
            <span class="tech-badge">Plotly</span>
            <span class="tech-badge">HTML/CSS/JS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid #475569; border-radius: 12px; padding: 1.5rem;">
        <h4 style="color: #f1f5f9; margin-bottom: 1rem;">📊 Data Processing</h4>
        <div class="tech-stack">
            <span class="tech-badge">TF-IDF</span>
            <span class="tech-badge">NLP</span>
            <span class="tech-badge">API Integration</span>
            <span class="tech-badge">Multi-format</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Features
st.markdown("<h3 style='color: #f1f5f9; margin-top: 3rem; margin-bottom: 1.5rem;'>✨ Key Features</h3>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid #475569; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
        <h4 style="color: #6366f1;">🎯 Ensemble Anomaly Detection</h4>
        <p style="color: #cbd5e1;">Combines Isolation Forest and One-Class SVM for robust anomaly detection</p>
    </div>
    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid #475569; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
        <h4 style="color: #8b5cf6;">📝 NLP Similarity Analysis</h4>
        <p style="color: #cbd5e1;">Detects suspiciously similar tender descriptions using TF-IDF</p>
    </div>
    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid #475569; border-radius: 12px; padding: 1.5rem;">
        <h4 style="color: #6366f1;">🧠 SHAP Explainability</h4>
        <p style="color: #cbd5e1;">Provides transparent explanations for each anomaly detection</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid #475569; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
        <h4 style="color: #8b5cf6;">📊 Multi-Source Data Loading</h4>
        <p style="color: #cbd5e1;">Supports CSV, JSON, XML, API, and synthetic data generation</p>
    </div>
    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid #475569; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
        <h4 style="color: #6366f1;">📈 Interactive Visualizations</h4>
        <p style="color: #cbd5e1;">Real-time charts and dashboards for data exploration</p>
    </div>
    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid #475569; border-radius: 12px; padding: 1.5rem;">
        <h4 style="color: #8b5cf6;">⚡ Risk Score Calculation</h4>
        <p style="color: #cbd5e1;">Weighted fusion of multiple anomaly signals into actionable risk scores</p>
    </div>
    """, unsafe_allow_html=True)

# Contact/Links
st.markdown("<h3 style='color: #f1f5f9; margin-top: 3rem; margin-bottom: 1.5rem;'>🔗 Links & Resources</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid #475569; border-radius: 12px; padding: 1.5rem; text-align: center;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📂</div>
        <h4 style="color: #f1f5f9; margin-bottom: 0.5rem;">GitHub Repository</h4>
        <a href="https://github.com/ayushv-nitj/public-procurement-anomaly-detection" target="_blank" 
           style="color: #6366f1; text-decoration: none; font-weight: 600;">
            View Source Code →
        </a>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid #475569; border-radius: 12px; padding: 1.5rem; text-align: center;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📖</div>
        <h4 style="color: #f1f5f9; margin-bottom: 0.5rem;">Documentation</h4>
        <a href="https://github.com/ayushv-nitj/public-procurement-anomaly-detection#readme" target="_blank" 
           style="color: #8b5cf6; text-decoration: none; font-weight: 600;">
            Read Docs →
        </a>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: rgba(30, 41, 59, 0.6); border: 1px solid #475569; border-radius: 12px; padding: 1.5rem; text-align: center;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🌐</div>
        <h4 style="color: #f1f5f9; margin-bottom: 0.5rem;">Live Demo</h4>
        <a href="https://ayushv-nitj.github.io/public-procurement-anomaly-detection/" target="_blank" 
           style="color: #6366f1; text-decoration: none; font-weight: 600;">
            Try It Out →
        </a>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="margin-top: 5rem; padding: 2rem 0; border-top: 1px solid #334155; text-align: center;">
    <p style="color: #94a3b8; font-size: 0.9rem;">
        © 2024 Procurement Anomaly Detection System | Professional Lab Project
    </p>
    <p style="color: #64748b; font-size: 0.85rem; margin-top: 0.5rem;">
        Developed with ❤️ by Team Ayush Verma
    </p>
</div>
""", unsafe_allow_html=True)
