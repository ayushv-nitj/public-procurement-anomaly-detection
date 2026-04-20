# Public Procurement Anomaly Detection System

> AI-powered detection of suspicious patterns in government contracts — BTech CS Project

## What it does
- Detects anomalous contracts using Isolation Forest & One-Class SVM
- Flags high-risk vendors based on multi-signal scoring
- Computes a normalized risk score (0–100) per contract
- Explains predictions using SHAP values
- Displays everything on an interactive Streamlit dashboard

## Tech Stack
| Layer | Tools |
|---|---|
| Data | Pandas, synthetic CSV (500 rows) |
| Feature Engineering | Scikit-learn, FuzzyWuzzy |
| ML Models | Isolation Forest, One-Class SVM |
| NLP | TF-IDF + cosine similarity |
| Risk Scoring | Weighted combination (hardcoded) |
| Explainability | SHAP |
| Dashboard | Streamlit + Plotly |

## Project Structure
```
procurement-anomaly/
├── data/
│   └── generate_data.py        # synthetic dataset generator
├── src/
│   ├── features.py             # feature engineering
│   ├── models.py               # IF + SVM anomaly detection
│   ├── nlp.py                  # TF-IDF similarity
│   ├── risk_score.py           # score fusion (hardcoded weights)
│   └── explainer.py            # SHAP wrapper
├── dashboard/
│   └── app.py                  # Streamlit app (main entry)
├── requirements.txt
├── setup.md
└── README.md
```

## Quickstart
```bash
pip install -r requirements.txt
python data/generate_data.py       # creates data/contracts.csv
streamlit run dashboard/app.py
```

## Risk Score Formula
```
risk_score = 0.5 × anomaly_score
           + 0.3 × nlp_similarity_score
           + 0.2 × vendor_frequency_score
```
Scores are normalized to 0–100. Threshold: **≥ 70 = High risk**.

## Dataset Schema
| Column | Description |
|---|---|
| contract_id | Unique ID |
| vendor_name | Vendor (fuzzy-cleaned) |
| dept | Department |
| amount | Contract value (₹) |
| award_date | Date of award |
| description | Tender description text |
| risk_score | Computed (0–100) |
| is_anomaly | 0 or 1 |

## Limitations
- Synthetic data only (not real GeM data)
- Hardcoded thresholds (not learned)
- No network graph analysis (future scope)
- No Transformer embeddings (TF-IDF only)

## Future Scope
- Plug in real GeM / CAG data
- Add NetworkX graph analysis (vendor–dept network)
- Replace TF-IDF with sentence-transformers
- Self-training SVM for semi-supervised labelling
- CAG audit report integration
