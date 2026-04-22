# 🔍 Public Procurement Anomaly Detection System

> AI-powered detection of suspicious patterns in government procurement contracts — BTech CS Project

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-GitHub_Pages-blue?style=for-the-badge)](https://ayushv-nitj.github.io/public-procurement-anomaly-detection/)
[![Streamlit App](https://img.shields.io/badge/📊_Streamlit-Dashboard-red?style=for-the-badge)](https://public-procurement-anomaly-detection-atksofxwzcio5qeakrsqds.streamlit.app/)

---

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run with existing data (fastest)
python run_pipeline.py --source csv --filepath data/contracts.csv

# OR generate fresh synthetic data
python run_pipeline.py --source synthetic

# OR load from JSON/XML
python run_pipeline.py --source json --filepath data/sample_contracts.json

# OR fetch from API (requires API key)
python run_pipeline.py --source api --api-url "..." --api-key "..."

# View results
cd frontend && python -m http.server 8080  # Open http://localhost:8080
```

**📖 See [USAGE_GUIDE.md](USAGE_GUIDE.md) for detailed examples and API integration**

---

## Table of Contents

- [What This Project Does](#what-this-project-does)
- [Key Terminology](#key-terminology)
- [System Architecture](#system-architecture)
- [How the Pipeline Works (Step by Step)](#how-the-pipeline-works-step-by-step)
  - [Phase 1: Synthetic Data Generation](#phase-1-synthetic-data-generation)
  - [Phase 2: Feature Engineering](#phase-2-feature-engineering)
  - [Phase 3: Anomaly Detection (ML Models)](#phase-3-anomaly-detection-ml-models)
  - [Phase 4: NLP Similarity Analysis](#phase-4-nlp-similarity-analysis)
  - [Phase 5: Risk Score Fusion](#phase-5-risk-score-fusion)
  - [Phase 6: SHAP Explainability](#phase-6-shap-explainability)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Dataset Schema](#dataset-schema)
- [How to Run](#how-to-run)
- [Dashboards](#dashboards)
- [Results & Metrics](#results--metrics)
- [Risk Score Formula](#risk-score-formula)
- [Limitations & Future Scope](#limitations--future-scope)

---

## What This Project Does

Public procurement (government purchasing of goods and services) is a massive area prone to fraud, corruption, and inefficiency. This system automatically detects suspicious procurement contracts using machine learning and natural language processing.

**The system flags contracts that exhibit patterns like:**
- 💰 **Abnormally high amounts** for routine items (e.g., ₹200 Cr for office furniture)
- 🔄 **Suspiciously similar tender descriptions** (copy-paste tenders indicating potential bid-rigging)
- 🏢 **Vendor monopolies** — same vendor repeatedly winning contracts
- ⚡ **Rapid-fire awards** — multiple contracts to the same vendor in quick succession
- 📛 **Misspelled vendor names** — slight name variations used to hide repeat vendors

It then assigns each contract a **Risk Score (0–100)** and explains *why* each contract was flagged using SHAP (explainable AI).

---

## Key Terminology

Understanding these terms is essential before diving into the pipeline:

### Machine Learning Terms

| Term | What It Means |
|------|---------------|
| **Anomaly Detection** | Finding data points that don't fit the expected pattern. Unlike classification (where you train with labelled examples), anomaly detection is *unsupervised* — it learns what "normal" looks like and flags anything unusual. |
| **Isolation Forest** | A tree-based anomaly detection algorithm. It works by randomly selecting a feature and then randomly selecting a split value. Anomalies require fewer random splits to be "isolated" from the rest of the data, so they have shorter path lengths in the tree. |
| **One-Class SVM** | Support Vector Machine trained on normal data only. It learns a boundary around normal data in high-dimensional space. Anything falling outside this boundary is flagged as an anomaly. |
| **Ensemble** | Combining multiple models to get better results. In our case, we use a *union* strategy: a contract is flagged if **either** Isolation Forest **or** One-Class SVM flags it. This reduces the chance of missing anomalies. |
| **Contamination** | The expected proportion of anomalies in the data. We set this to 0.1 (10%), meaning we expect about 10% of contracts to be anomalous. |
| **Feature Engineering** | Transforming raw data into meaningful numerical features that ML models can learn from. Raw text and dates can't be fed directly into models — they need to be converted into numbers. |
| **Unsupervised Learning** | ML where the model learns patterns without labelled examples. We don't tell the model which contracts are fraudulent — it discovers unusual patterns on its own. |

### NLP Terms

| Term | What It Means |
|------|---------------|
| **TF-IDF** | *Term Frequency–Inverse Document Frequency*. A numerical representation of text. Words that appear frequently in one document but rarely across all documents get higher scores. For example, "radar systems" appearing in only 2 out of 500 contracts would get a high TF-IDF score. |
| **Cosine Similarity** | Measures how similar two text vectors are by computing the cosine of the angle between them. Ranges from 0 (completely different) to 1 (identical). Two contract descriptions with cosine similarity > 0.8 are flagged as suspiciously similar. |
| **N-grams** | Sequences of N consecutive words. Unigrams = single words ("supply"), bigrams = word pairs ("annual maintenance"). Using bigrams helps capture phrases like "solar panels" as a single unit. |
| **Stop Words** | Common words like "the", "is", "at" that carry no meaningful information. These are removed before vectorizing text. |
| **Vectorization** | Converting text into numerical vectors (arrays of numbers) that ML algorithms can process. |

### Explainability Terms

| Term | What It Means |
|------|---------------|
| **SHAP (SHapley Additive exPlanations)** | A game-theory based approach to explain individual predictions. For each contract, SHAP tells you how much each feature contributed to the anomaly score. Named after Shapley values from cooperative game theory. |
| **SHAP Value** | The contribution of each feature to a specific prediction. Positive SHAP = pushes prediction toward "anomaly". Negative SHAP = pushes toward "normal". |
| **TreeExplainer** | A fast SHAP algorithm optimized for tree-based models like Isolation Forest. Computes exact SHAP values in polynomial time. |
| **Global Feature Importance** | The average |SHAP value| across all contracts for each feature. Shows which features are most influential *overall*. |

### Statistical Terms

| Term | What It Means |
|------|---------------|
| **Z-Score** | How many standard deviations a value is from the mean. A z-score of 3 means the value is 3 standard deviations above the mean — very unusual. We compute z-scores for contract amounts within each department. |
| **Normalization** | Scaling values to a standard range (usually 0–1 or 0–100) so that features with different scales can be compared fairly. |
| **Min-Max Scaling** | A normalization technique: `(value - min) / (max - min)`. Maps the smallest value to 0 and the largest to 1. |
| **Standard Scaling** | Transforms features to have mean=0 and standard deviation=1. Required for algorithms like SVM that are sensitive to feature scales. |
| **Log-Normal Distribution** | A probability distribution where the logarithm of values follows a normal distribution. Used for contract amounts because real financial data is typically right-skewed (many small amounts, few very large ones). |

### Procurement Terms

| Term | What It Means |
|------|---------------|
| **Procurement** | The process by which government departments purchase goods, services, or works from vendors through competitive bidding. |
| **Tender** | A formal invitation to vendors to submit bids for a contract. Each tender has a description of what is being procured. |
| **Contract** | A legally binding agreement between a government department and a vendor. |
| **Bid Rigging** | An illegal practice where competing vendors coordinate their bids to ensure a pre-selected vendor wins. |
| **GeM** | Government e-Marketplace — India's online platform for government procurement. |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA INPUT LAYER (NEW!)                      │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Synthetic   │  │   CSV File   │  │  JSON File   │         │
│  │  Generator   │  │              │  │              │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                 │                  │
│  ┌──────┴───────┐  ┌──────┴───────────────────────┐           │
│  │  XML File    │  │  Government API (data.gov.in) │           │
│  │              │  │  Requires: API Key + Approval │           │
│  └──────┬───────┘  └──────┬───────────────────────┘           │
│         │                 │                                    │
│         └─────────┬───────┴──────────┐                         │
│                   ▼                  ▼                         │
│         ┌─────────────────────────────────┐                    │
│         │   src/data_loader.py            │                    │
│         │   - Auto column normalization   │                    │
│         │   - Format conversion           │                    │
│         │   - Schema validation           │                    │
│         └─────────────┬─────────────────┘                      │
└───────────────────────┼─────────────────────────────────────────┘
                        │
                        ▼
              data/contracts.csv (standardized)
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FEATURE ENGINEERING LAYER                     │
│                      src/features.py                            │
│                                                                 │
│  Raw CSV → vendor_freq, amount_zscore, days_since_last,         │
│            amount_dept_ratio, vendor_encoded, dept_encoded       │
│         → StandardScaler → Feature Matrix (N × 7)               │
└──────────┬──────────────────┬───────────────────────────────────┘
           │                  │
           ▼                  ▼
┌──────────────────┐  ┌──────────────────┐
│  ANOMALY MODELS  │  │   NLP ANALYSIS   │
│  src/models.py   │  │   src/nlp.py     │
│                  │  │                  │
│ Isolation Forest │  │ TF-IDF Vectors   │
│ One-Class SVM    │  │ Cosine Similarity│
│ Ensemble Scores  │  │ Similar Pairs    │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RISK SCORE FUSION                             │
│                    src/risk_score.py                             │
│                                                                 │
│  risk = 0.5 × anomaly_score + 0.3 × nlp_score + 0.2 × vendor   │
│  Normalized to 0–100, threshold ≥ 70 = "High Risk"              │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXPLAINABILITY LAYER                          │
│                    src/explainer.py                              │
│                                                                 │
│  SHAP TreeExplainer → per-contract explanations                 │
│  Global feature importance → mean |SHAP|                        │
└───────────────────────┬─────────────────────────────────────────┘
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
┌──────────────────┐        ┌──────────────────┐
│ FRONTEND (8080)  │        │ STREAMLIT (8501)  │
│ HTML + CSS + JS  │        │ Python + Plotly   │
│ Chart.js         │        │ Interactive SHAP  │
│ Static Dashboard │        │ Live Pipeline     │
└──────────────────┘        └──────────────────┘
```

---

## How the Pipeline Works (Step by Step)

### Phase 1: Synthetic Data Generation
**File:** `data/generate_data.py`

Since we don't have access to real government procurement data (GeM data is restricted), we generate a **realistic synthetic dataset** of 500 contracts.

**What happens:**
1. Creates **450 normal contracts** with:
   - Vendor names from a pool of 42 real Indian companies (TCS, Infosys, L&T, BHEL, etc.)
   - 12 government departments (Defence, Railways, Health, etc.)
   - Amounts following a **log-normal distribution** (₹1 Lakh to ₹50 Crore) — this mirrors real procurement data where most contracts are small and a few are very large
   - Random dates across 2 years (2022–2023)
   - Realistic tender descriptions generated from templates

2. Injects **50 anomalous contracts** (~10%) with four types of anomalies:

| Anomaly Type | What It Does | Why It's Suspicious |
|---|---|---|
| **Inflated Amount** | Sets amount to ₹60Cr–₹200Cr for routine items | Way above the normal range for the item type |
| **Suspicious Vendor** | Uses misspelled vendor names ("Infossys", "Wiproo") | Real-world tactic to hide repeated vendor selection |
| **Duplicate Description** | Uses vague, near-identical descriptions | Indicates copy-paste tenders (potential bid-rigging) |
| **Rapid-Fire Award** | Multiple contracts to same vendor within 0–3 days | Suggests splitting large contracts to avoid oversight |

3. Shuffles all records and exports to `data/contracts.csv`

---

### Phase 2: Feature Engineering
**File:** `src/features.py`

Raw data (vendor names, dates, text) cannot be fed directly into ML models. This module transforms each contract into a **vector of 7 numerical features**.

**Features computed:**

| # | Feature | How It's Computed | What It Captures |
|---|---------|-------------------|------------------|
| 1 | `amount` | Direct value (₹) | Contract size |
| 2 | `vendor_freq` | Count of contracts per vendor | Vendor monopoly — vendors with unusually many contracts |
| 3 | `amount_zscore` | `(amount - dept_mean) / dept_std` | How unusual the amount is *within the same department*. A contract of ₹100Cr might be normal for Defence but extremely unusual for Education. |
| 4 | `days_since_last` | Days between this and the vendor's previous contract | Rapid-fire awarding — very low values (0–3 days) are suspicious |
| 5 | `amount_dept_ratio` | `amount / dept_median` | How many times larger this contract is compared to the department's typical contract |
| 6 | `vendor_encoded` | Label-encoded vendor name (integer) | Categorical encoding for ML models |
| 7 | `dept_encoded` | Label-encoded department (integer) | Categorical encoding for ML models |

**After computing all features:**
- Apply **StandardScaler** (mean=0, std=1) so all features are on the same scale
- Output: a **500 × 7 feature matrix** ready for ML

---

### Phase 3: Anomaly Detection (ML Models)
**File:** `src/models.py`

We use two complementary unsupervised anomaly detection algorithms and combine them in an ensemble.

#### Algorithm 1: Isolation Forest

**Core idea:** Anomalies are "few and different", so they can be isolated with fewer random partitions.

**How it works:**
1. Randomly select a feature (e.g., `amount`)
2. Randomly select a split value between the feature's min and max
3. Split the data: values < split go left, values ≥ split go right
4. Repeat recursively until each point is isolated
5. **Anomalies need fewer splits** to be isolated (shorter path length = more anomalous)

**Configuration:**
```python
IsolationForest(
    n_estimators=200,     # 200 random trees in the forest
    contamination=0.1,    # expect ~10% anomalies
    max_samples="auto",   # use min(256, n_samples) per tree
    random_state=42       # reproducibility
)
```

**Output:**
- `predictions`: -1 (anomaly) or 1 (normal) for each contract
- `scores`: continuous anomaly score (more negative = more anomalous)

#### Algorithm 2: One-Class SVM

**Core idea:** Learn a boundary that encloses all "normal" data. Anything outside the boundary is anomalous.

**How it works:**
1. Maps data into a higher-dimensional space using the **RBF (Radial Basis Function) kernel**
2. Finds the smallest hypersphere that contains most of the training data
3. Points outside this hypersphere are flagged as anomalies

**Configuration:**
```python
OneClassSVM(
    kernel="rbf",    # Radial Basis Function — handles non-linear boundaries
    gamma="scale",   # auto-compute kernel coefficient
    nu=0.1           # upper bound on fraction of outliers (10%)
)
```

**Why use this alongside Isolation Forest?**
- Isolation Forest excels with **global anomalies** (extreme values)
- One-Class SVM is better at detecting **local anomalies** (subtle deviations in dense regions)
- Together, they catch more types of anomalies

#### Ensemble (Combining Both Models)

```
ensemble_label = IF_anomaly  OR  SVM_anomaly   (union strategy)

ensemble_score = 0.6 × IF_normalized_score + 0.4 × SVM_normalized_score
```

- **Union strategy**: A contract is flagged if *either* model flags it. This favours recall (catching all anomalies) over precision.
- **Score normalization**: Both models produce scores on different scales, so we normalize each to [0, 1] before combining.
- **IF gets 60% weight** because tree-based models generally perform better on tabular data.

---

### Phase 4: NLP Similarity Analysis
**File:** `src/nlp.py`

This module detects **suspiciously similar tender descriptions** that may indicate copy-paste tenders or coordinated bidding.

**Step-by-step process:**

1. **TF-IDF Vectorization:**
   - Each contract description is converted into a numerical vector
   - Words that are common across all descriptions (e.g., "supply", "contract") get low weights
   - Words that are unique to a few descriptions (e.g., "radar systems") get high weights
   - We use both **unigrams** (single words) and **bigrams** (word pairs)
   - Stop words (the, is, at, etc.) are removed
   - Result: a **500 × 500 sparse matrix** (500 contracts × up to 500 features)

2. **Cosine Similarity:**
   - For every pair of contracts, compute how similar their TF-IDF vectors are
   - Result: a **500 × 500 similarity matrix**
   - Self-similarity (diagonal) is set to 0

3. **Per-contract NLP score:**
   - For each contract, take the **maximum similarity** with any other contract
   - This becomes the NLP score (0 to 1)
   - Higher means this contract's description is very similar to at least one other contract

4. **Suspicious pairs:**
   - Any pair with similarity ≥ 0.8 is flagged
   - These pairs are shown in the dashboard for manual review

**Why this matters:**
In real procurement fraud, vendors sometimes submit near-identical descriptions across multiple tenders. This is a red flag for **bid rigging** — where vendors coordinate to ensure a predetermined winner.

---

### Phase 5: Risk Score Fusion
**File:** `src/risk_score.py`

The three signals (anomaly score, NLP similarity, vendor frequency) are combined into a single **Risk Score (0–100)**.

**Formula:**
```
risk_score = 0.50 × anomaly_score_normalized
           + 0.30 × nlp_similarity_normalized
           + 0.20 × vendor_frequency_normalized
```

**Step-by-step:**
1. **Normalize** each signal to 0–100 using min-max scaling
2. **Weighted sum** with the above weights
3. **Clip** to [0, 100] range
4. **Threshold**: risk_score ≥ 70 → **"High Risk"**, otherwise → **"Low Risk"**

**Why these weights?**
| Signal | Weight | Reasoning |
|--------|--------|-----------|
| Anomaly Score | 50% | The ML ensemble is the primary anomaly detector — it captures multi-dimensional patterns |
| NLP Similarity | 30% | Description similarity is a strong independent signal for bid-rigging |
| Vendor Frequency | 20% | Vendor monopoly is a risk factor, but some vendors legitimately win many contracts |

---

### Phase 6: SHAP Explainability
**File:** `src/explainer.py`

SHAP makes the model's decisions **transparent and interpretable** — essential for government audit use cases.

**How SHAP works (conceptually):**
- Based on **Shapley values** from cooperative game theory
- Treats each feature as a "player" in a "game" (the prediction)
- Computes each feature's marginal contribution by evaluating all possible subsets of features
- Result: for each contract, each feature gets a SHAP value showing its positive or negative contribution

**What we compute:**

1. **Per-contract SHAP values:** For any flagged contract, see which features drove the anomaly prediction
   - Example: *"CTR-0042 was flagged because `amount` had a SHAP value of +0.38 (very high) and `days_since_last` had +0.22 (very low gap between contracts)"*

2. **Global feature importance:** Average |SHAP value| across all contracts
   - Shows which features are most influential *overall* in detecting anomalies

**Why this matters:**
An AI system flagging government contracts must be **explainable**. Auditors need to understand *why* a contract was flagged, not just that it was flagged. SHAP provides that transparency.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Data Generation | Pandas, NumPy | Synthetic dataset with injected anomalies |
| Feature Engineering | Scikit-learn (StandardScaler, LabelEncoder) | Transform raw data → numerical features |
| Anomaly Detection | Scikit-learn (IsolationForest, OneClassSVM) | Unsupervised outlier detection |
| NLP | Scikit-learn (TfidfVectorizer, cosine_similarity) | Text similarity analysis |
| Risk Scoring | NumPy | Weighted signal fusion |
| Explainability | SHAP (TreeExplainer) | Feature importance explanations |
| Streamlit Dashboard | Streamlit, Plotly | Interactive Python dashboard |
| Frontend Dashboard | HTML, CSS, JavaScript, Chart.js | Premium static dashboard |
| Deployment | GitHub Pages, GitHub Actions | Live hosting for frontend |

---

## Project Structure

```
public-procurement-anomaly-detection/
│
├── data/
│   ├── generate_data.py        # Synthetic dataset generator (450 normal + 50 anomalous)
│   ├── contracts.csv           # Generated dataset (500 rows × 6 columns)
│   ├── sample_contracts.json   # Sample JSON format for testing
│   └── sample_contracts.xml    # Sample XML format for testing
│
├── src/
│   ├── __init__.py             # Makes src a Python package
│   ├── data_loader.py          # NEW: Multi-source data loader (CSV/JSON/XML/API/Synthetic)
│   ├── features.py             # Feature engineering (7 features + scaling)
│   ├── models.py               # Isolation Forest + One-Class SVM ensemble
│   ├── nlp.py                  # TF-IDF vectorization + cosine similarity
│   ├── risk_score.py           # Weighted risk score fusion (0–100)
│   └── explainer.py            # SHAP TreeExplainer wrapper
│
├── dashboard/
│   └── app.py                  # Streamlit interactive dashboard
│
├── frontend/
│   ├── index.html              # Premium dark-themed dashboard page
│   ├── styles.css              # Glassmorphism CSS with animations
│   ├── app.js                  # Chart.js visualizations + interactive table
│   └── results.json            # Pipeline output consumed by frontend
│
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions → GitHub Pages deployment
│
├── run_pipeline.py             # NEW: Enhanced with multi-source support + CLI args
├── test_data_sources.py        # NEW: Test script for all data sources
├── requirements.txt            # Python dependencies (added: requests)
├── USAGE_GUIDE.md              # NEW: Comprehensive usage guide for all data sources
├── setup.md                    # Detailed setup guide
├── walkthrough.md              # Development walkthrough
└── README.md                   # This file
```

---

## Dataset Schema

### Supported Data Sources

The application now supports **5 data input methods**:

| Source | Use Case | Command Example |
|--------|----------|-----------------|
| **Synthetic** | Demo/testing with realistic fake data | `--source synthetic` |
| **CSV** | Local CSV files | `--source csv --filepath data/contracts.csv` |
| **JSON** | Local JSON files | `--source json --filepath data/contracts.json` |
| **XML** | Local XML files | `--source xml --filepath data/contracts.xml` |
| **API** | Live government data portals | `--source api --api-url "..." --api-key "..."` |

### Column Name Flexibility

The data loader automatically normalizes column names. You can use any of these variations:

| Standard Column | Accepted Variations |
|----------------|---------------------|
| `contract_id` | id, contract_number, tender_id |
| `vendor_name` | vendor, supplier, contractor, company |
| `dept` | department, ministry, agency |
| `amount` | value, contract_value, price, cost |
| `award_date` | date, contract_date, award |
| `description` | desc, title, tender_description, item |

### Raw Data (`data/contracts.csv`)

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| `contract_id` | String | CTR-0042 | Unique identifier for each contract |
| `vendor_name` | String | Tata Consulting Services | Name of the vendor awarded the contract |
| `dept` | String | Ministry of Defence | Government department issuing the contract |
| `amount` | Float | 12345678.90 | Contract value in INR (₹) |
| `award_date` | Date | 2023-06-15 | Date the contract was awarded |
| `description` | String | Supply of network equipment for... | Tender description text |

### Computed Columns (after pipeline)

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `vendor_freq` | Integer | 1–30+ | How many contracts this vendor has been awarded |
| `amount_zscore` | Float | -3 to +10 | Z-score of amount within the same department |
| `days_since_last` | Float | 0–730 | Days since this vendor's previous contract |
| `amount_dept_ratio` | Float | 0.01–100+ | Ratio of amount to department median |
| `is_anomaly` | Binary | 0 or 1 | 1 if flagged by the ensemble model |
| `anomaly_score` | Float | 0–1 | Continuous anomaly score from ensemble |
| `nlp_similarity` | Float | 0–1 | Max cosine similarity with any other contract |
| `risk_score` | Float | 0–100 | Final fused risk score |
| `risk_label` | String | High / Low | High if risk_score ≥ 70 |

---

## How to Run

### Prerequisites
- Python 3.9+
- pip

### Setup (first time only)

```bash
# Clone the repository
git clone https://github.com/ayushv-nitj/public-procurement-anomaly-detection.git
cd public-procurement-anomaly-detection

# Create and activate virtual environment
python -m venv venv

# Activate:
# Windows (Git Bash):
source ./venv/Scripts/activate
# Windows (PowerShell):
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run the pipeline

The pipeline now supports **multiple data sources**: synthetic generation, CSV, JSON, XML, and API.

#### Option 1: Use existing CSV data (default)
```bash
python run_pipeline.py --source csv --filepath data/contracts.csv
```

#### Option 2: Generate synthetic data
```bash
# First generate the data
python data/generate_data.py

# Then run pipeline
python run_pipeline.py --source synthetic
```

#### Option 3: Load from JSON file
```bash
python run_pipeline.py --source json --filepath data/sample_contracts.json
```

#### Option 4: Load from XML file
```bash
python run_pipeline.py --source xml --filepath data/sample_contracts.xml
```

#### Option 5: Fetch from API (e.g., Government Open Data)
```bash
# Example with Indian Government Open Data API
python run_pipeline.py --source api \
  --api-url "https://api.data.gov.in/resource/YOUR_RESOURCE_ID" \
  --api-key "YOUR_API_KEY" \
  --format json \
  --limit 100
```

**API Parameters:**
- `--api-url`: Full API endpoint URL (required)
- `--api-key`: API key for authentication (optional, if required by API)
- `--format`: Response format - json/xml/csv (optional)
- `--offset`: Pagination offset (default: 0)
- `--limit`: Maximum records to fetch (default: 100)

**Note:** For Government Open Data APIs that require access approval, you'll need to:
1. Register on the data portal (e.g., data.gov.in)
2. Request access from the data officer
3. Generate an API key from your account
4. Use the API key in the command above

### View Results

```bash
# View the premium frontend dashboard
cd frontend && python -m http.server 8080
# Open http://localhost:8080

# View the Streamlit interactive dashboard (in a separate terminal)
streamlit run dashboard/app.py
# Opens http://localhost:8501
```

> **Note:** The frontend dashboard requires an HTTP server — opening `index.html` directly via `file://` will fail due to browser CORS restrictions on `fetch()`.

---

## Dashboards

### 🎨 Frontend Dashboard (Port 8080)
Premium dark-themed static dashboard built with vanilla HTML/CSS/JS and Chart.js.

**Features:**
- Animated KPI counter cards (Total Contracts, Anomalies, High Risk, Avg Risk Score, Anomaly Rate)
- Risk Score Distribution histogram with gradient coloring
- Anomalies by Department horizontal bar chart
- SHAP Global Feature Importance chart
- Top 15 Risky Vendors ranked list with color-coded scores
- Interactive contracts table with search, department/risk filters, column sorting, and pagination
- Risk Score Formula visualization
- Floating particle background animation
- Glassmorphism card effects
- Fully responsive design

### 🔬 Streamlit Dashboard (Port 8501)
Interactive Python dashboard with Plotly charts.

**Features:**
- All visualizations from the frontend, plus:
- **Per-contract SHAP explainer** — select any flagged contract and see which features drove its anomaly score
- **Suspiciously similar pairs table** — side-by-side comparison of near-duplicate descriptions
- **Interactive scatter plot** — contract amount vs risk score with hover details
- Live pipeline execution (re-runs models on each load)

---

## Results & Metrics

| Metric | Value |
|--------|-------|
| Total Contracts Analyzed | 500 |
| Anomalies Detected (Ensemble) | 66 |
| High Risk Contracts (≥70) | 14 |
| Average Risk Score | 41.9 |
| Anomaly Rate | 13.2% |

The ensemble detects more anomalies (66) than the 50 injected ones because some normal contracts also exhibit unusual patterns — this is expected behavior in unsupervised anomaly detection.

---

## Risk Score Formula

```
risk_score = 0.50 × anomaly_score + 0.30 × nlp_similarity + 0.20 × vendor_frequency
```

Each component is normalized to 0–100 before fusion. The final score is clipped to [0, 100].

| Component | Weight | Source |
|-----------|--------|--------|
| Anomaly Score | 50% | Isolation Forest + One-Class SVM ensemble (captures multi-dimensional statistical anomalies) |
| NLP Similarity | 30% | TF-IDF cosine similarity (detects copy-paste tenders and bid-rigging signals) |
| Vendor Frequency | 20% | Contract count per vendor (flags vendor monopolies) |

**Threshold:** Score ≥ 70 → **High Risk** (requires manual audit review)

---

## Limitations & Future Scope

### Current Limitations
- **Synthetic data only** — not trained on real GeM/government procurement data
- **Hardcoded weights** — the 50/30/20 weights in risk scoring are set manually, not learned from data
- **No network analysis** — doesn't analyze vendor–department relationship graphs
- **TF-IDF only** — doesn't use modern transformer embeddings for deeper semantic understanding
- **No temporal modeling** — doesn't account for seasonal spending patterns

### API Integration Notes

The application is **ready to work with government procurement APIs** like:
- **India:** data.gov.in Open Government Data Platform
- **USA:** USAspending.gov API
- **UK:** Contracts Finder API
- **EU:** Tenders Electronic Daily (TED)

**Important:** Most government APIs require:
1. User registration on the data portal
2. Access approval from data officers (can take 1-7 days)
3. API key generation from your account dashboard

**Example API workflow:**
```bash
# 1. Register at data.gov.in and request access
# 2. Generate API key from "My Account" → "API Key"
# 3. Find resource ID from dataset page URL
# 4. Run pipeline:
python run_pipeline.py --source api \
  --api-url "https://api.data.gov.in/resource/RESOURCE_ID" \
  --api-key "YOUR_API_KEY" \
  --format json --limit 500
```

The data loader handles common API response formats automatically and normalizes column names to match the expected schema.

### Future Scope
- 🔌 Plug in real GeM (Government e-Marketplace) data via their API
- 🕸️ Add **NetworkX graph analysis** to detect vendor–department collusion networks
- 🤖 Replace TF-IDF with **sentence-transformers** (e.g., `all-MiniLM-L6-v2`) for better semantic similarity
- 📈 Implement **time-series anomaly detection** for seasonal spending patterns
- 🏷️ Use **semi-supervised learning** with a small set of confirmed fraud labels
- 📋 Integrate **CAG (Comptroller and Auditor General) audit reports** as ground truth
- 🌐 Add real-time monitoring with automated alerts for new suspicious contracts

---

## License

This project is for academic purposes (BTech CS Project).

---

## Author

**Ayush Verma** — NIT Jamshedpur
