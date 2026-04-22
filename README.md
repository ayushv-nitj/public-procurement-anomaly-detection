# 🔍 Public Procurement Anomaly Detection System

> AI-powered detection of suspicious patterns in government procurement contracts

[![Streamlit App](https://img.shields.io/badge/📊_Streamlit-Dashboard-red?style=for-the-badge)](https://public-procurement-anomaly-detection-atksofxwzcio5qeakrsqds.streamlit.app/)


<img width="1487" height="967" alt="Screenshot 2026-04-23 030314" src="https://github.com/user-attachments/assets/f6b10941-3756-4ec6-a25b-f6aa5f271418" />
<img width="1496" height="694" alt="Screenshot 2026-04-23 030359" src="https://github.com/user-attachments/assets/7bdd63c9-a3b8-4831-b9c2-014f8741a247" />
<img width="1524" height="708" alt="Screenshot 2026-04-23 030337" src="https://github.com/user-attachments/assets/54cc8e27-babc-4cf2-b00a-b1fcf74ae035" />




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

<img width="1894" height="981" alt="Screenshot 2026-04-23 030230" src="https://github.com/user-attachments/assets/9b9e99e6-f3ab-4295-9e48-50e9e56c4be4" />

---

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

### Core Machine Learning Terms

| Term | What It Means | Why It Matters |
|------|---------------|----------------|
| **Supervised Learning** | Training a model with labeled data (input-output pairs). Example: Given contracts labeled as "fraud" or "normal", learn to predict labels for new contracts. | Most accurate when you have labeled data, but requires expensive manual labeling. |
| **Unsupervised Learning** | ML where the model learns patterns without labeled examples. We don't tell the model which contracts are fraudulent — it discovers unusual patterns on its own. | Perfect for anomaly detection where labeled fraud examples are rare or unavailable. |
| **Semi-Supervised Learning** | Combines small amount of labeled data with large amount of unlabeled data. Example: Use 50 confirmed fraud cases + 10,000 unlabeled contracts. | Best of both worlds — improves accuracy with minimal labeling effort. |
| **Training Set** | The data used to train the model. The model learns patterns from this data. | Typically 70-80% of total data. Quality matters more than quantity. |
| **Test Set** | Data held back to evaluate model performance. Never seen during training. | Simulates real-world performance. If test accuracy << training accuracy, model is overfitting. |
| **Overfitting** | When a model memorizes training data instead of learning general patterns. Performs well on training data but poorly on new data. | Prevented by: cross-validation, regularization, more training data, simpler models. |
| **Underfitting** | When a model is too simple to capture the underlying patterns. Performs poorly on both training and test data. | Fixed by: more complex models, better features, more training iterations. |
| **Hyperparameters** | Settings that control how a model learns (e.g., number of trees in forest, learning rate). Set before training, not learned from data. | Tuned using grid search or random search. Example: `n_estimators=200` in Isolation Forest. |
| **Cross-Validation** | Splitting data into K folds, training on K-1 folds and testing on the remaining fold. Repeat K times. | Gives more reliable performance estimates than single train-test split. We use K=5. |
| **Bias-Variance Tradeoff** | Bias = error from wrong assumptions (underfitting). Variance = error from sensitivity to training data (overfitting). Goal: minimize both. | High bias → model too simple. High variance → model too complex. Sweet spot in the middle. |

### Anomaly Detection Specific Terms

| Term | What It Means | Technical Details |
|------|---------------|-------------------|
| **Anomaly Detection** | Finding data points that don't fit the expected pattern. Unlike classification (where you train with labeled examples), anomaly detection is *unsupervised* — it learns what "normal" looks like and flags anything unusual. | Also called: outlier detection, novelty detection, one-class classification. Used in: fraud detection, network intrusion, medical diagnosis. |
| **Isolation Forest** | A tree-based anomaly detection algorithm. It works by randomly selecting a feature and then randomly selecting a split value. Anomalies require fewer random splits to be "isolated" from the rest of the data, so they have shorter path lengths in the tree. | **Time Complexity:** O(n log n) for training. **Space:** O(n). **Advantages:** Fast, handles high dimensions, no distance calculations. **Disadvantages:** Assumes anomalies are "few and different". |
| **One-Class SVM** | Support Vector Machine trained on normal data only. It learns a boundary around normal data in high-dimensional space. Anything falling outside this boundary is flagged as an anomaly. | **Kernel:** RBF (Radial Basis Function) maps data to infinite dimensions. **Nu parameter:** Upper bound on fraction of outliers (we use 0.1 = 10%). **Advantages:** Handles non-linear boundaries. **Disadvantages:** Slow on large datasets, sensitive to scaling. |
| **Ensemble** | Combining multiple models to get better results. In our case, we use a *union* strategy: a contract is flagged if **either** Isolation Forest **or** One-Class SVM flags it. This reduces the chance of missing anomalies. | **Strategies:** Union (OR logic, high recall), Intersection (AND logic, high precision), Voting (majority wins), Weighted average. We use union to maximize anomaly detection. |
| **Contamination** | The expected proportion of anomalies in the data. We set this to 0.1 (10%), meaning we expect about 10% of contracts to be anomalous. | **Impact:** Higher contamination → more points flagged. Lower → fewer flags. Should match domain knowledge. Real fraud rates: credit cards ~0.1%, insurance ~5-10%. |
| **Anomaly Score** | Continuous value indicating how anomalous a point is. Higher score = more anomalous. Threshold determines binary classification. | **Isolation Forest:** Based on path length (shorter = more anomalous). **One-Class SVM:** Distance from decision boundary (farther = more anomalous). |
| **Local vs Global Anomalies** | **Local:** Anomalous within a neighborhood but not globally. **Global:** Anomalous compared to entire dataset. | Example: ₹10Cr contract is global anomaly. ₹10Cr in Defence is normal, but in Education is local anomaly. We detect both types. |

### Feature Engineering Terms

| Term | What It Means | Implementation Details |
|------|---------------|------------------------|
| **Feature Engineering** | Transforming raw data into meaningful numerical features that ML models can learn from. Raw text and dates can't be fed directly into models — they need to be converted into numbers. | **Process:** Domain knowledge → feature ideas → implementation → validation. Good features can improve accuracy by 10-50%. |
| **Feature Extraction** | Creating new features from raw data. Example: From date, extract day_of_week, month, is_weekend. | **Techniques:** Aggregations (sum, mean, count), transformations (log, sqrt), interactions (feature1 × feature2). |
| **Feature Selection** | Choosing which features to keep and which to discard. Removes irrelevant/redundant features. | **Methods:** Correlation analysis, mutual information, recursive feature elimination, LASSO regularization. |
| **Feature Scaling** | Transforming features to similar ranges so no single feature dominates. | **StandardScaler:** (x - mean) / std → mean=0, std=1. **MinMaxScaler:** (x - min) / (max - min) → range [0,1]. **RobustScaler:** Uses median and IQR, robust to outliers. |
| **Label Encoding** | Converting categorical variables (text) to integers. Example: "Defence"→0, "Health"→1, "Education"→2. | **Limitation:** Implies ordering (Defence < Health < Education) which may not exist. Alternative: One-hot encoding. |
| **One-Hot Encoding** | Converting categorical variable to binary columns. "Defence" → [1,0,0], "Health" → [0,1,0]. | **Advantage:** No false ordering. **Disadvantage:** High dimensionality (K categories → K columns). Use when K < 10-20. |
| **Dimensionality Reduction** | Reducing number of features while preserving information. Example: 100 features → 10 principal components. | **Techniques:** PCA (linear), t-SNE (non-linear, visualization), UMAP (fast, preserves structure). |

### Natural Language Processing (NLP) Terms

| Term | What It Means | Mathematical Foundation |
|------|---------------|-------------------------|
| **Tokenization** | Splitting text into individual units (tokens). Usually words, but can be characters or subwords. | Example: "Supply of laptops" → ["Supply", "of", "laptops"]. Handles punctuation, contractions, special characters. |
| **Stop Words** | Common words like "the", "is", "at" that carry no meaningful information. These are removed before vectorizing text. | **Standard list:** ~150-200 words. **Custom:** Domain-specific (e.g., "contract", "supply" in procurement). Removal improves signal-to-noise ratio. |
| **Stemming** | Reducing words to their root form. "running", "runs", "ran" → "run". Fast but crude. | **Algorithm:** Porter Stemmer (most common). **Limitation:** "university" → "univers" (not a real word). |
| **Lemmatization** | Reducing words to dictionary form using linguistic rules. "running" → "run", "better" → "good". Slower but accurate. | **Requires:** Part-of-speech tagging. **Tool:** WordNet. **Advantage:** Always produces valid words. |
| **N-grams** | Sequences of N consecutive words. Unigrams = single words ("supply"), bigrams = word pairs ("annual maintenance"). Using bigrams helps capture phrases like "solar panels" as a single unit. | **Formula:** Text of length L has (L - N + 1) N-grams. **Trade-off:** Higher N captures more context but increases dimensionality exponentially. |
| **Bag of Words (BoW)** | Represents text as unordered collection of words, ignoring grammar and word order. | **Example:** "cat sat on mat" and "mat on sat cat" have identical BoW representations. Simple but loses context. |
| **TF-IDF** | *Term Frequency–Inverse Document Frequency*. A numerical representation of text. Words that appear frequently in one document but rarely across all documents get higher scores. For example, "radar systems" appearing in only 2 out of 500 contracts would get a high TF-IDF score. | **Formula:** TF-IDF(word, doc) = TF(word, doc) × IDF(word). **TF:** (count of word in doc) / (total words in doc). **IDF:** log(total docs / docs containing word). **Range:** 0 to ~10. |
| **Cosine Similarity** | Measures how similar two text vectors are by computing the cosine of the angle between them. Ranges from 0 (completely different) to 1 (identical). Two contract descriptions with cosine similarity > 0.8 are flagged as suspiciously similar. | **Formula:** cos(θ) = (A · B) / (‖A‖ × ‖B‖). **Advantage:** Ignores magnitude, only considers direction. "I love cats" and "I love love love cats" are very similar despite different lengths. |
| **Vectorization** | Converting text into numerical vectors (arrays of numbers) that ML algorithms can process. | **Methods:** Count vectors (word frequencies), TF-IDF vectors (weighted frequencies), Word embeddings (dense semantic vectors). |
| **Sparse Matrix** | Matrix where most values are zero. TF-IDF produces sparse matrices (most words don't appear in most documents). | **Storage:** Only store non-zero values. **Advantage:** Memory efficient. 500 docs × 5000 words = 2.5M values, but only ~50K non-zero. |
| **Word Embeddings** | Dense vector representations where semantically similar words have similar vectors. "king" - "man" + "woman" ≈ "queen". | **Models:** Word2Vec (Google), GloVe (Stanford), FastText (Facebook). **Dimension:** Typically 50-300. **Advantage:** Captures semantic relationships. |
| **Sentence Embeddings** | Vector representation of entire sentences/paragraphs. Captures meaning beyond individual words. | **Models:** BERT, Sentence-BERT, Universal Sentence Encoder. **Use case:** Better than TF-IDF for semantic similarity. Future enhancement for this project. |

### Deep Learning Terms (Future Enhancements)

| Term | What It Means | Potential Application |
|------|---------------|----------------------|
| **Neural Network** | ML model inspired by brain structure. Layers of interconnected neurons that learn hierarchical representations. | **For this project:** Could replace TF-IDF with LSTM/Transformer for description analysis. Better semantic understanding. |
| **LSTM (Long Short-Term Memory)** | Type of recurrent neural network that can learn long-term dependencies in sequences. | **Use case:** Analyze temporal patterns in contract sequences. Detect unusual timing patterns across multiple contracts. |
| **Transformer** | Modern neural architecture using attention mechanism. Foundation of BERT, GPT. | **Use case:** Fine-tune BERT on procurement text to detect subtle fraud indicators in descriptions. |
| **Attention Mechanism** | Allows model to focus on relevant parts of input. "Which words in description are most important for fraud detection?" | **Advantage:** Interpretable — can visualize which words model focuses on. Better than black-box TF-IDF. |
| **Transfer Learning** | Using a model pre-trained on large dataset and fine-tuning on your specific task. | **Example:** Start with BERT trained on Wikipedia, fine-tune on procurement contracts. Requires less labeled data. |
| **Autoencoder** | Neural network that learns to compress data and reconstruct it. Anomalies have high reconstruction error. | **Use case:** Alternative to Isolation Forest. Learn normal contract patterns, flag contracts that can't be reconstructed well. |
| **GAN (Generative Adversarial Network)** | Two networks competing: Generator creates fake data, Discriminator tries to detect fakes. | **Use case:** Generate synthetic fraudulent contracts for training. Augment limited fraud examples. |

### Explainability & Interpretability Terms

| Term | What It Means | Why Critical for Government AI |
|------|---------------|-------------------------------|
| **Explainable AI (XAI)** | ML models that can explain their decisions in human-understandable terms. | **Legal requirement:** Government decisions must be explainable. "Computer said so" is not acceptable in court. |
| **SHAP (SHapley Additive exPlanations)** | A game-theory based approach to explain individual predictions. For each contract, SHAP tells you how much each feature contributed to the anomaly score. Named after Shapley values from cooperative game theory. | **Properties:** Consistent (if feature helps, SHAP value is positive), Local accuracy (explanations sum to prediction), Missingness (missing features have zero impact). |
| **SHAP Value** | The contribution of each feature to a specific prediction. Positive SHAP = pushes prediction toward "anomaly". Negative SHAP = pushes toward "normal". | **Interpretation:** SHAP value of +0.3 for `amount` means this feature increased anomaly score by 0.3. Larger magnitude = more influential. |
| **TreeExplainer** | A fast SHAP algorithm optimized for tree-based models like Isolation Forest. Computes exact SHAP values in polynomial time. | **Speed:** O(TLD²) where T=trees, L=leaves, D=depth. Much faster than model-agnostic methods. **Accuracy:** Exact, not approximate. |
| **Global Feature Importance** | The average |SHAP value| across all contracts for each feature. Shows which features are most influential *overall*. | **Use case:** "Amount is the most important feature for detecting anomalies across all contracts." Guides feature engineering priorities. |
| **Local Explanation** | Explanation for a single prediction. "Why was THIS contract flagged?" | **Example:** "Contract CTR-042 flagged because: amount (+0.38), days_since_last (+0.22), vendor_freq (+0.15)." |
| **Feature Attribution** | Assigning credit/blame to each input feature for a prediction. | **Methods:** SHAP, LIME, Integrated Gradients, Attention weights. SHAP is theoretically grounded (Shapley values). |
| **Counterfactual Explanation** | "What would need to change for the prediction to flip?" Example: "If amount was ₹5Cr instead of ₹50Cr, contract would not be flagged." | **Advantage:** Actionable. Tells you exactly what to change. **Challenge:** Finding realistic counterfactuals. |

### Statistical & Mathematical Terms

| Term | What It Means | Formula & Interpretation |
|------|---------------|--------------------------|
| **Z-Score (Standard Score)** | How many standard deviations a value is from the mean. A z-score of 3 means the value is 3 standard deviations above the mean — very unusual. We compute z-scores for contract amounts within each department. | **Formula:** z = (x - μ) / σ. **Interpretation:** |z| > 2 is unusual (~5% of data), |z| > 3 is very unusual (~0.3% of data). |
| **Standard Deviation (σ)** | Measure of spread/variability in data. Low σ = data clustered near mean. High σ = data spread out. | **Formula:** σ = sqrt(Σ(x - μ)² / N). **Units:** Same as original data. ₹10Cr mean with ₹2Cr std means most contracts are ₹8-12Cr. |
| **Mean (μ) vs Median** | **Mean:** Average (sum / count). Sensitive to outliers. **Median:** Middle value. Robust to outliers. | **Example:** Salaries [30K, 35K, 40K, 1M]. Mean = 276K (misleading). Median = 37.5K (representative). Use median for skewed data. |
| **Normalization** | Scaling values to a standard range (usually 0–1 or 0–100) so that features with different scales can be compared fairly. | **Why needed:** Amount (₹1L-50Cr) and days_since_last (0-730) have different scales. Without normalization, amount dominates. |
| **Min-Max Scaling** | A normalization technique: `(value - min) / (max - min)`. Maps the smallest value to 0 and the largest to 1. | **Formula:** x' = (x - x_min) / (x_max - x_min). **Range:** [0, 1]. **Limitation:** Sensitive to outliers (one extreme value affects all). |
| **Standard Scaling (Z-score normalization)** | Transforms features to have mean=0 and standard deviation=1. Required for algorithms like SVM that are sensitive to feature scales. | **Formula:** x' = (x - μ) / σ. **Range:** Typically [-3, +3] but unbounded. **Advantage:** Preserves outliers (unlike min-max). |
| **Log-Normal Distribution** | A probability distribution where the logarithm of values follows a normal distribution. Used for contract amounts because real financial data is typically right-skewed (many small amounts, few very large ones). | **Properties:** Always positive, right-skewed, multiplicative processes. **Example:** If log(amount) ~ Normal(μ, σ), then amount ~ LogNormal. |
| **Correlation** | Measures linear relationship between two variables. Ranges from -1 (perfect negative) to +1 (perfect positive). 0 = no linear relationship. | **Formula:** r = Σ((x - x̄)(y - ȳ)) / sqrt(Σ(x - x̄)² × Σ(y - ȳ)²). **Interpretation:** |r| > 0.7 is strong, 0.3-0.7 is moderate, < 0.3 is weak. |
| **Covariance** | Measures how two variables change together. Positive = both increase together. Negative = one increases, other decreases. | **Formula:** cov(X,Y) = Σ((x - x̄)(y - ȳ)) / N. **Limitation:** Scale-dependent. Correlation is normalized covariance. |
| **Precision vs Recall** | **Precision:** Of flagged contracts, how many are actually fraudulent? (TP / (TP + FP)). **Recall:** Of all fraudulent contracts, how many did we flag? (TP / (TP + FN)). | **Trade-off:** High precision = few false alarms but miss some fraud. High recall = catch all fraud but many false alarms. We optimize for recall (union ensemble). |
| **F1 Score** | Harmonic mean of precision and recall. Balances both metrics. | **Formula:** F1 = 2 × (precision × recall) / (precision + recall). **Range:** [0, 1]. **Use:** Single metric when you care equally about precision and recall. |

### Procurement Domain Terms

| Term | What It Means | Fraud Indicators |
|------|---------------|------------------|
| **Procurement** | The process by which government departments purchase goods, services, or works from vendors through competitive bidding. | **Fraud types:** Bid rigging, kickbacks, inflated pricing, phantom vendors, split purchases. |
| **Tender** | A formal invitation to vendors to submit bids for a contract. Each tender has a description of what is being procured. | **Red flags:** Vague descriptions, short bidding windows, restrictive specifications favoring one vendor. |
| **Contract** | A legally binding agreement between a government department and a vendor. | **Suspicious patterns:** Repeated amendments, cost overruns, delayed deliveries, substandard quality. |
| **Bid Rigging** | An illegal practice where competing vendors coordinate their bids to ensure a pre-selected vendor wins. | **Detection:** Similar bid amounts, identical typos in bids, vendors taking turns winning, complementary bidding. |
| **GeM (Government e-Marketplace)** | India's online platform for government procurement. Mandatory for purchases below ₹25 Lakh. | **Data:** 50+ Lakh products, 60 Lakh orders, ₹1 Lakh Crore+ transactions. Restricted access for research. |
| **Single Source Procurement** | Awarding contract without competition. Legal in emergencies or for specialized items. | **Abuse:** Fake emergencies, inflated prices, vendor favoritism. Requires strong justification. |
| **Split Purchases** | Breaking large purchase into smaller ones to avoid oversight thresholds. | **Example:** ₹10Cr purchase split into 10 × ₹1Cr to avoid approval requirements. **Detection:** Multiple similar contracts in short time. |

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
├── 📂 data/                         # Data Files
│   ├── generate_data.py             # Synthetic dataset generator (450 normal + 50 anomalous)
│   ├── contracts.csv                # Generated dataset (500 rows × 6 columns) [gitignored]
│   ├── sample_contracts.json        # Sample JSON format for testing
│   ├── sample_contracts.xml         # Sample XML format for testing
│   └── README.md                    # Data documentation
│
├── 📂 src/                          # Core ML Pipeline (Backend Logic)
│   ├── __init__.py                  # Makes src a Python package
│   ├── data_loader.py               # Multi-source data loader (CSV/JSON/XML/API/Synthetic)
│   ├── features.py                  # Feature engineering (7 features + scaling)
│   ├── models.py                    # Isolation Forest + One-Class SVM ensemble
│   ├── nlp.py                       # TF-IDF vectorization + cosine similarity
│   ├── risk_score.py                # Weighted risk score fusion (0–100)
│   └── explainer.py                 # SHAP TreeExplainer wrapper
│
├── 📂 dashboard/                    # Streamlit Apps (Python UI)
│   ├── app.py                       # Full-featured interactive dashboard ⭐
│   ├── app_basic.py                 # Basic Streamlit dashboard (backup)
│   └── pages/
│       └── about.py                 # About page with team info
│
├── 📂 frontend/                     # Static Web Interface (HTML/CSS/JS)
│   ├── index.html                   # Upload interface
│   ├── dashboard.html               # Dashboard view
│   ├── upload.js                    # Upload logic and API calls
│   ├── app.js                       # Chart.js visualizations + interactive table
│   ├── styles.css                   # Glassmorphism CSS with animations
│   └── results.json                 # Pipeline output [gitignored]
│
├── 📂 docs/                         # Documentation
│   ├── setup.md                     # Detailed setup guide
│   ├── walkthrough.md               # Development walkthrough
│   ├── DEMO_SCRIPT.md               # Demo guide for presentations
│   ├── COMPLETE_WORKFLOW.md         # Complete workflow guide
│   ├── DEPLOYMENT.md                # Deployment guide
│   └── PROJECT_STRUCTURE.md         # Project structure documentation
│
├── 📂 tests/                        # Test Files
│   ├── __init__.py                  # Makes tests a Python package
│   └── test_data_sources.py         # Test script for all data sources
│
├── 📂 assets/                       # Images and Media
│   └── procurement_dashboard_ui.svg # UI mockup/diagram
│
├── 📂 .github/                      # GitHub Configuration
│   └── workflows/
│       └── deploy.yml               # GitHub Actions → GitHub Pages deployment
│
├── 📂 .streamlit/                   # Streamlit Configuration
│   └── config.toml                  # Theme and server settings
│
├── 📂 .devcontainer/                # Dev Container Configuration
│   └── devcontainer.json            # VS Code dev container setup
│
├── 📄 app.py                        # Flask backend server (for upload interface)
├── 📄 run_pipeline.py               # CLI pipeline runner with multi-source support
├── 📄 start_servers.py              # Start Flask + Frontend servers
├── 📄 requirements.txt              # Python dependencies
├── 📄 .gitignore                    # Git ignore rules
├── 📄 USAGE_GUIDE.md                # Comprehensive usage guide
└── 📄 README.md                     # This file (main documentation)
```

**Key Folders**:
- **`src/`** - Core ML pipeline (backend logic)
- **`dashboard/`** - Streamlit apps (Python UI) - **Recommended for deployment**
- **`frontend/`** - Static HTML/CSS/JS (web interface)
- **`docs/`** - All documentation in one place
- **`tests/`** - Test files
- **`assets/`** - Images and media files

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

### 🎨 Interactive Streamlit Dashboard (Port 8501) - **RECOMMENDED**
Modern, feature-rich dashboard with complete navigation and team information.

**Run:**
```bash
streamlit run dashboard/app.py
# OR
start_streamlit_interactive.bat
```

**New Features:**
- **🔝 Top Navbar**: GitHub link and About Us button for easy navigation
- **👥 About Us Page**: Complete team information, project details, and tech stack
- **📊 Multi-Source Data Loading**: Select from 5 data sources (Synthetic, CSV, JSON, XML, API)
- **🎨 Modern Dark Theme**: Bluish-black gradient with purple accents
- **📱 Redesigned Sidebar**: Better styling with icons, sections, and team info
- **🔗 Footer**: Team info, quick links, contact information, and social links
- **⚡ Real-time Processing**: Upload data and see results instantly

**Visualizations:**
- Risk Score Distribution with color coding (Low/High)
- Anomalies by Department horizontal bar chart
- SHAP Global Feature Importance
- **Per-contract SHAP explainer** — select any flagged contract and see which features drove its anomaly score
- **Suspiciously similar pairs table** — side-by-side comparison of near-duplicate descriptions
- **Interactive scatter plot** — contract amount vs risk score with hover details
- Flagged contracts table with filtering and sorting

**Data Source Options:**
1. **Generate Synthetic** - Creates 500 new random contracts each time
2. **Upload CSV** - Drag & drop or browse CSV files
3. **Upload JSON** - Load JSON format data
4. **Upload XML** - Load XML format data
5. **Fetch from API** - Connect to government data portals (requires API credentials)

### 🎨 Frontend Dashboard (Port 8080)
Premium dark-themed static dashboard built with vanilla HTML/CSS/JS and Chart.js.

**Run:**
```bash
cd frontend && python -m http.server 8080
```

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

### 🔬 Flask Backend API (Port 8080)
RESTful API for processing procurement data from multiple sources.

**Run:**
```bash
python app.py
```

**Features:**
- `/api/process` endpoint for data processing
- Supports all 5 data sources
- Server-side processing for security
- JSON response with anomaly detection results
- CORS support for frontend integration

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

**Team Leader:** Ayush Verma  
**Team Members:** Ishaan Rai, Priyanshu Raj, Aditya Prakash  
**Institution:** NIT Jamshedpur 
**Project Type:** Professional Lab Project

**GitHub Repository:** [https://github.com/ayushv-nitj/public-procurement-anomaly-detection](https://github.com/ayushv-nitj/public-procurement-anomaly-detection)

---

## 🚀 Complete Application Workflow

The application provides **three different interfaces** for maximum flexibility:

### 1. Upload Interface (Port 8080) - Best for Demos & File Uploads

**Start:**
```bash
python start_servers.py
```

**Access:** http://localhost:8080

**Features:**
- Modern drag & drop file upload interface
- Support for all 5 data sources (Synthetic, CSV, JSON, XML, API)
- Real-time processing with progress indicators
- Automatic redirect to dashboard after analysis
- Clean separation: Port 5000 (API) + Port 8080 (Frontend)

**Workflow:**
1. Open http://localhost:8080 (upload interface is the default page)
2. Select data source from 5 options
3. Upload file (drag & drop or browse) OR enter API credentials
4. Click "Analyze" button
5. View summary statistics
6. Click "View Full Dashboard" → redirects to http://localhost:8080/dashboard.html
7. Explore interactive visualizations

**Architecture:**
```
Browser (8080) → Upload Page → POST to Flask API (5000)
                                      ↓
                              ML Pipeline Processing
                                      ↓
                              Results Saved
                                      ↓
Browser (8080) ← Dashboard Page ← Results Loaded
```

### 2. Streamlit Dashboard (Port 8501) - Best for Interactive Analysis

**Start:**
```bash
streamlit run dashboard/app.py
```

**Access:** http://localhost:8501

**Features:**
- All-in-one interface with sidebar controls
- File upload directly in sidebar (no separate upload page)
- Real-time processing and visualization
- Top navbar with GitHub link and About Us button
- About Us page with complete team information
- Footer with team info and quick links
- Modern dark theme with bluish-black gradient

**How to Upload in Streamlit:**
1. Look at the **LEFT SIDEBAR**
2. Find dropdown: "Select Data Source"
3. Choose your source (CSV/JSON/XML/Synthetic/API)
4. File uploader appears below the dropdown
5. Click "Browse files" or drag & drop
6. Data processes automatically
7. Results appear in main area immediately

**Navigation:**
- Click "About Us" in top navbar to see team information
- Click "GitHub" to view source code
- Scroll to footer for quick links and contact info

### 3. Command Line Interface - Best for Automation

**Run:**
```bash
# Synthetic data
python run_pipeline.py --source synthetic

# CSV file
python run_pipeline.py --source csv --filepath data/contracts.csv

# JSON file
python run_pipeline.py --source json --filepath data/sample_contracts.json

# XML file
python run_pipeline.py --source xml --filepath data/sample_contracts.xml

# API
python run_pipeline.py --source api \
  --api-url "https://api.data.gov.in/resource/RESOURCE_ID" \
  --api-key "YOUR_API_KEY" \
  --format json --limit 100
```

**Features:**
- Batch processing
- Scriptable and automatable
- Results saved to `frontend/results.json`
- Terminal output with statistics
- Perfect for CI/CD pipelines

---

## 📊 Comparison: Which Interface to Use?

| Feature | Upload Interface (8080) | Streamlit (8501) | Command Line |
|---------|------------------------|------------------|--------------|
| **Best For** | Demos, presentations | Interactive analysis | Automation, scripts |
| **File Upload** | ✅ Drag & drop | ✅ Browse in sidebar | ❌ File path only |
| **Real-time** | ✅ Yes | ✅ Yes | ❌ Batch |
| **Visualizations** | ✅ Dashboard page | ✅ Interactive charts | ❌ None |
| **Navigation** | ✅ Multi-page | ✅ Navbar + pages | ❌ Terminal only |
| **Team Info** | ❌ No | ✅ About Us page | ❌ No |
| **Setup** | 2 servers (Flask + HTTP) | 1 server (Streamlit) | No server |
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 🎯 Quick Start Guide

### For Professor Demo (Recommended):
```bash
# Option 1: Upload Interface
python start_servers.py
# Open: http://localhost:8080
# Upload data → View dashboard

# Option 2: Streamlit
streamlit run dashboard/app.py
# Open: http://localhost:8501
# Use sidebar to upload → See results immediately
```

### For Development:
```bash
# Generate new synthetic data
python data/generate_data.py

# Run pipeline
python run_pipeline.py --source synthetic

# View results
cd frontend && python -m http.server 8080
```

### For Testing All Data Sources:
```bash
# Test all 5 data sources
python test_data_sources.py
```

---

## 📖 Additional Documentation

- **QUICK_REFERENCE.md** - Quick command reference for all features
- **docs/DEMO_SCRIPT.md** - Step-by-step demo guide for presentations
- **docs/COMPLETE_WORKFLOW.md** - Detailed explanation of all three workflows
- **docs/DEPLOYMENT.md** - Deployment guide for Streamlit Cloud and GitHub Pages
- **NAVIGATION_FEATURES.md** - UI enhancements and navigation guide
- **docs/setup.md** - Detailed setup instructions
- **docs/walkthrough.md** - Development walkthrough
- **docs/PROJECT_STRUCTURE.md** - Project structure and organization

---

## 🔧 Technical Architecture

### Backend (Flask API - Port 5000)
- **Purpose:** Process data and run ML pipeline
- **Endpoints:**
  - `/api/process` - Process uploaded data
  - `/api/save-results` - Save results to file
  - `/api/sample-data/<type>` - Get sample data
- **Security:** API keys handled server-side, not exposed to browser
- **CORS:** Enabled for frontend communication

### Frontend (HTTP Server - Port 8080)
- **Purpose:** Serve HTML/CSS/JS files
- **Pages:**
  - `index.html` - Upload interface (default page)
  - `dashboard.html` - Results dashboard
- **Technology:** Vanilla JavaScript, Chart.js, modern CSS
- **Features:** Drag & drop, responsive design, animations

### Streamlit (Port 8501)
- **Purpose:** All-in-one interactive dashboard
- **Technology:** Python, Streamlit, Plotly
- **Features:** File upload, real-time processing, SHAP explanations
- **Navigation:** Multi-page with navbar and footer

---

## 🎨 UI/UX Features

### Modern Dark Theme
- **Background:** Bluish-black gradient (#0a0e27 → #1a1f3a → #0f1419)
- **Sidebar:** Purple gradient (#6366f1 → #8b5cf6)
- **Accents:** Indigo and violet
- **Typography:** Inter font family
- **Contrast:** High contrast for accessibility

### Navigation Elements
- **Top Navbar:** Fixed position with GitHub link and About Us button
- **Sidebar:** Redesigned with icons, sections, and team info
- **Footer:** Team information, quick links, contact details
- **About Us Page:** Complete team profiles and project information

### Interactive Elements
- **Drag & Drop:** File upload with visual feedback
- **Hover Effects:** Smooth transitions on buttons and cards
- **Loading States:** Spinners and progress indicators
- **Error Handling:** Clear error messages with suggestions
- **Responsive:** Works on desktop, tablet, and mobile

---

## 🔐 Security Considerations

### API Key Handling
- API keys are processed server-side (Flask backend)
- Never exposed in browser or frontend JavaScript
- Stored temporarily only during request processing
- Not logged or persisted

### Data Privacy
- All processing happens locally (no external services)
- Uploaded files are stored in temporary directories
- Temporary files are deleted after processing
- No data is sent to third-party servers

### Input Validation
- File type validation (CSV, JSON, XML only)
- File size limits to prevent memory issues
- API URL validation
- SQL injection prevention (no database queries)
- XSS prevention (sanitized outputs)

---

## 🐛 Troubleshooting

### Common Issues

**1. "ModuleNotFoundError: No module named 'flask'"**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**2. "Port already in use"**
```bash
# Solution: Kill process on port
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

**3. "CORS error" in browser console**
```bash
# Solution: Make sure Flask backend is running
python app.py

# And flask-cors is installed
pip install flask-cors
```

**4. "File upload not working in Streamlit"**
- Check that you've selected a data source from the dropdown first
- File uploader appears in the SIDEBAR, not main area
- Look below the "Select Data Source" dropdown

**5. "API request failed: 400 Bad Request"**
- Verify API URL is correct
- Check if API key is valid
- Ensure you have access approval from data portal
- Try reducing the limit parameter

**6. "Dashboard shows no data"**
- Check if `frontend/results.json` exists
- Try running the pipeline again
- Clear browser cache and reload

---

## 📞 Support & Contact

**Team:**
- **Leader:** Ayush Verma
- **Members:** Ishaan Rai, Priyanshu Raj, Aditya Prakash

**Institution:** NIT Jamshedpur 
**Project Type:** Professional Lab Project

**Repository:** [https://github.com/ayushv-nitj/public-procurement-anomaly-detection](https://github.com/ayushv-nitj/public-procurement-anomaly-detection)

**For Issues:**
- Open an issue on GitHub
- Check existing documentation files
- Review troubleshooting section above

---

## 🙏 Acknowledgments

- **Data Source Inspiration:** Government e-Marketplace (GeM) India
- **ML Techniques:** Scikit-learn documentation and research papers
- **UI Design:** Modern web design principles and best practices
- **Explainability:** SHAP library and interpretable ML research

---

## License

This project is for academic purposes (BTech CS Project).
