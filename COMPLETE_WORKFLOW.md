# 🔄 Complete Application Workflow

## Overview

This document explains the complete workflow of the Procurement Anomaly Detection System with all interfaces.

---

## 🎯 Three Ways to Use the Application

### 1. **Upload Interface (Port 8080)** - Best for File Uploads
### 2. **Streamlit Dashboard (Port 8501)** - Best for Interactive Analysis
### 3. **Command Line** - Best for Batch Processing

---

## 📊 Workflow 1: Upload Interface (Port 8080)

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    USER WORKFLOW                             │
└─────────────────────────────────────────────────────────────┘

Step 1: Start Servers
┌──────────────────────┐
│ start_upload_        │
│ interface.bat        │
└──────────┬───────────┘
           │
           ├─────────────────────────────────────┐
           │                                     │
           ▼                                     ▼
┌──────────────────────┐              ┌──────────────────────┐
│  Flask Backend       │              │  Frontend Server     │
│  Port 5000           │              │  Port 8080           │
│  (API Processing)    │              │  (Static Files)      │
└──────────────────────┘              └──────────────────────┘

Step 2: Upload Data
┌──────────────────────────────────────────────────────────────┐
│  Browser: http://localhost:8080/upload.html                  │
│                                                               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │Synthetic│  │   CSV   │  │  JSON   │  │   XML   │  │API│ │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
│       │            │            │            │               │
│       └────────────┴────────────┴────────────┘               │
│                    │                                          │
│                    ▼                                          │
│         ┌──────────────────────┐                             │
│         │  Click "Analyze"     │                             │
│         └──────────┬───────────┘                             │
└────────────────────┼──────────────────────────────────────────┘
                     │
                     ▼
Step 3: Processing
┌──────────────────────────────────────────────────────────────┐
│  POST http://localhost:5000/api/process                      │
│                                                               │
│  Flask Backend:                                               │
│  ├─ Load data (src/data_loader.py)                          │
│  ├─ Build features (src/features.py)                         │
│  ├─ Run ML models (src/models.py)                            │
│  ├─ NLP analysis (src/nlp.py)                                │
│  ├─ Calculate risk scores (src/risk_score.py)                │
│  └─ Return JSON results                                       │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ▼
Step 4: View Results
┌──────────────────────────────────────────────────────────────┐
│  Upload Page Shows Summary:                                   │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌───────────┐│
│  │   Total    │ │ Anomalies  │ │ High Risk  │ │ Avg Risk  ││
│  │ Contracts  │ │  Detected  │ │   Count    │ │   Score   ││
│  └────────────┘ └────────────┘ └────────────┘ └───────────┘│
│                                                               │
│  ┌──────────────────────────────────────────┐               │
│  │  📊 View Full Dashboard  │  🔄 New Data  │               │
│  └──────────────┬───────────────────────────┘               │
└─────────────────┼──────────────────────────────────────────┘
                  │
                  ▼
Step 5: Dashboard
┌──────────────────────────────────────────────────────────────┐
│  Browser: http://localhost:8080/index.html                   │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  KPI Cards | Risk Distribution | Dept Analysis      │    │
│  │  Feature Importance | Top Vendors | Contracts Table │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

### Quick Start
```bash
# One command to start everything
python start_servers.py

# Then open in browser
http://localhost:8080
```

---

## 📊 Workflow 2: Streamlit Dashboard (Port 8501)

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    USER WORKFLOW                             │
└─────────────────────────────────────────────────────────────┘

Step 1: Start Streamlit
┌──────────────────────┐
│ streamlit run        │
│ dashboard/           │
│ app_interactive.py   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Streamlit Server    │
│  Port 8501           │
│  (All-in-one)        │
└──────────────────────┘

Step 2: Access Dashboard
┌──────────────────────────────────────────────────────────────┐
│  Browser: http://localhost:8501                              │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  🔝 Top Navbar                                       │    │
│  │  [🔍 Procurement] [📂 GitHub] [👥 About Us]        │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  ┌──────────┐  ┌────────────────────────────────────┐       │
│  │ Sidebar  │  │  Main Content Area                 │       │
│  │          │  │                                     │       │
│  │ 📊 Data  │  │  📊 Visualizations                 │       │
│  │ Source   │  │  📈 Charts                         │       │
│  │          │  │  📋 Tables                         │       │
│  │ Upload   │  │  🧠 SHAP Analysis                  │       │
│  │ Area     │  │                                     │       │
│  │          │  │                                     │       │
│  │ 👥 Team  │  │                                     │       │
│  │ Info     │  │                                     │       │
│  └──────────┘  └────────────────────────────────────┘       │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  🔗 Footer: Team | Links | Tech Stack | Contact    │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘

Step 3: Select Data Source
┌──────────────────────────────────────────────────────────────┐
│  Sidebar Dropdown:                                            │
│  ┌─────────────────────────────────────┐                     │
│  │ ▼ Select Data Source                │                     │
│  │   • Generate Synthetic               │                     │
│  │   • Upload CSV                       │                     │
│  │   • Upload JSON                      │                     │
│  │   • Upload XML                       │                     │
│  │   • Fetch from API                   │                     │
│  └─────────────────────────────────────┘                     │
└──────────────────────────────────────────────────────────────┘

Step 4: Upload/Generate
┌──────────────────────────────────────────────────────────────┐
│  For Files: Drag & drop or browse                            │
│  For Synthetic: Click "Generate & Analyze"                   │
│  For API: Enter URL, key, format, limit                      │
│                                                               │
│  Processing happens in real-time within Streamlit            │
└──────────────────────────────────────────────────────────────┘

Step 5: View Results
┌──────────────────────────────────────────────────────────────┐
│  All visualizations appear immediately:                       │
│  • Summary metrics                                            │
│  • Risk distribution                                          │
│  • Department analysis                                        │
│  • SHAP importance                                            │
│  • Per-contract explanations                                  │
│  • Similar descriptions                                       │
│  • Scatter plots                                              │
└──────────────────────────────────────────────────────────────┘
```

### Quick Start
```bash
# Start Streamlit
streamlit run dashboard/app_interactive.py

# Or use batch file
start_streamlit_interactive.bat

# Then open in browser
http://localhost:8501
```

---

## 📊 Workflow 3: Command Line (Batch Processing)

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    COMMAND LINE WORKFLOW                     │
└─────────────────────────────────────────────────────────────┘

Step 1: Run Pipeline
┌──────────────────────────────────────────────────────────────┐
│  python run_pipeline.py --source <SOURCE> [OPTIONS]         │
│                                                               │
│  Sources:                                                     │
│  • csv --filepath data/contracts.csv                         │
│  • json --filepath data/sample_contracts.json                │
│  • xml --filepath data/sample_contracts.xml                  │
│  • synthetic (no file needed)                                │
│  • api --api-url URL --api-key KEY --format json --limit 100│
└──────────────────────────────────────────────────────────────┘
           │
           ▼
Step 2: Processing
┌──────────────────────────────────────────────────────────────┐
│  Pipeline Execution:                                          │
│  ├─ Load data                                                │
│  ├─ Build features                                           │
│  ├─ Run models                                               │
│  ├─ NLP analysis                                             │
│  ├─ Calculate risk scores                                    │
│  ├─ SHAP explanations                                        │
│  └─ Save to frontend/results.json                           │
└──────────────────────┬────────────────────────────────────────┘
                       │
                       ▼
Step 3: View Results
┌──────────────────────────────────────────────────────────────┐
│  Terminal Output:                                             │
│  • Total contracts loaded                                     │
│  • Features created                                           │
│  • Anomalies detected                                         │
│  • Risk scores calculated                                     │
│  • Results saved                                              │
│                                                               │
│  Then open dashboard:                                         │
│  cd frontend && python -m http.server 8080                   │
│  http://localhost:8080/index.html                            │
└──────────────────────────────────────────────────────────────┘
```

### Quick Start
```bash
# Generate synthetic data
python run_pipeline.py --source synthetic

# Upload CSV
python run_pipeline.py --source csv --filepath data/contracts.csv

# View results
cd frontend && python -m http.server 8080
```

---

## 🔀 Comparison: Which to Use?

| Feature | Upload Interface | Streamlit | Command Line |
|---------|-----------------|-----------|--------------|
| **Port** | 8080 | 8501 | N/A |
| **File Upload** | ✅ Drag & drop | ✅ Browse | ❌ File path only |
| **Real-time** | ✅ Yes | ✅ Yes | ❌ Batch |
| **Visualizations** | ✅ Dashboard | ✅ Interactive | ❌ None |
| **Navigation** | ✅ Multi-page | ✅ Multi-page | ❌ Terminal |
| **Team Info** | ❌ No | ✅ About page | ❌ No |
| **Best For** | Demos, uploads | Analysis, exploration | Automation |
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🎯 Recommended Workflows

### For Professor Demo
```
1. Use Upload Interface (Port 8080)
   - Most visual and impressive
   - Shows complete workflow
   - Easy to understand

Command: start_upload_interface.bat
URL: http://localhost:8080/upload.html
```

### For Data Analysis
```
2. Use Streamlit Dashboard (Port 8501)
   - Interactive exploration
   - Real-time updates
   - SHAP explanations

Command: streamlit run dashboard/app_interactive.py
URL: http://localhost:8501
```

### For Automation
```
3. Use Command Line
   - Batch processing
   - Scripting
   - CI/CD integration

Command: python run_pipeline.py --source synthetic
```

---

## 📁 Data Flow Summary

```
┌─────────────┐
│  User Input │
└──────┬──────┘
       │
       ├─────────────────────────────────────┐
       │                                     │
       ▼                                     ▼
┌──────────────┐                    ┌──────────────┐
│ Upload UI    │                    │  Streamlit   │
│ (Port 8080)  │                    │ (Port 8501)  │
└──────┬───────┘                    └──────┬───────┘
       │                                   │
       ▼                                   │
┌──────────────┐                          │
│ Flask API    │                          │
│ (Port 5000)  │                          │
└──────┬───────┘                          │
       │                                   │
       └───────────────┬───────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  ML Pipeline    │
              │  • data_loader  │
              │  • features     │
              │  • models       │
              │  • nlp          │
              │  • risk_score   │
              │  • explainer    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Results        │
              │  • JSON         │
              │  • localStorage │
              │  • results.json │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Dashboard      │
              │  • Visualize    │
              │  • Analyze      │
              │  • Export       │
              └─────────────────┘
```

---

## 🚀 Quick Commands Reference

```bash
# Upload Interface (Port 8080) - Works everywhere
python start_servers.py

# Streamlit Dashboard (Port 8501)
streamlit run dashboard/app_interactive.py

# Command Line Processing
python run_pipeline.py --source synthetic

# Flask Backend Only
python app.py

# Frontend Server Only
cd frontend && python -m http.server 8080
```

---

## 📞 Support

See detailed guides:
- `UPLOAD_INTERFACE_GUIDE.md` - Upload interface details
- `DEMO_SCRIPT.md` - Demo walkthrough
- `QUICK_REFERENCE.md` - Quick commands
- `README.md` - Full documentation

---

**Team**: Ayush Verma, Ishaan Rai, Priyanshu Raj, Aditya Prakash  
**Repository**: https://github.com/ayushv-nitj/public-procurement-anomaly-detection
