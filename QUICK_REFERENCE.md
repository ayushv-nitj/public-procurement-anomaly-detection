# Quick Reference Card

## 🚀 Run Commands


```bash
# Activate environment
source ./venv/Scripts/activate  # Git Bash
# OR
.\venv\Scripts\activate  # PowerShell
```bash



# 1️⃣ CSV (Default - 500 contracts)
python run_pipeline.py --source csv --filepath data/contracts.csv

# 2️⃣ Synthetic (Generate Fresh Data - NEW every time!)
python run_pipeline.py --source synthetic

# 3️⃣ JSON (50 contracts - Indian PSU vendors)
python run_pipeline.py --source json --filepath data/sample_contracts.json

# 4️⃣ XML (50 contracts - IT companies, DIFFERENT data than JSON)
python run_pipeline.py --source xml --filepath data/sample_contracts.xml

# 5️⃣ API (Government Data)
python run_pipeline.py --source api \
  --api-url "https://api.data.gov.in/resource/RESOURCE_ID" \
  --api-key "YOUR_API_KEY" \
  --format json --limit 100
```

**Show the API example from the image:**

"Based on the Government Open Data API you showed me, here's how we'd integrate it:"

```bash
python run_pipeline.py --source api \
  --api-url "https://api.data.gov.in/resource/e4d07942-2bd1-4167-bf91-fe4f29c82313" \
  --api-key "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b" \
  --format json \
  --offset 0 \
  --limit 100
```

## 🎲 Data Differences

| Source | Contracts | Results | Data Changes |
|--------|-----------|---------|--------------|
| CSV | 500 | ~65-70 anomalies | ✅ NEW each run |
| JSON | 50 | ~8 anomalies | ❌ Fixed |
| XML | 50 | ~10 anomalies | ❌ Fixed (different from JSON) |
| Synthetic | 500 | ~65-70 anomalies | ✅ NEW each run |

## 📊 View Results

```bash
# Frontend Dashboard
cd frontend && python -m http.server 8080
# → http://localhost:8080

# Streamlit Dashboard
streamlit run dashboard/app.py
# → http://localhost:8501
```

## 🧪 Test All Sources

```bash
python test_data_sources.py
```

## 📋 Required Columns

Your data must have these 6 columns (names can vary):

| Required | Variations Accepted |
|----------|-------------------|
| contract_id | id, contract_number, tender_id |
| vendor_name | vendor, supplier, contractor |
| dept | department, ministry, agency |
| amount | value, price, cost |
| award_date | date, contract_date |
| description | desc, title, item |

## 🔑 API Setup Steps

1. Register at data.gov.in
2. Request access (1-7 days)
3. Generate API key
4. Find resource ID from dataset URL
5. Run command with credentials

**⚠️ IMPORTANT:** The API keys and resource IDs shown in examples are PLACEHOLDERS. They will NOT work. You must:
- Register your own account
- Request access approval
- Generate YOUR OWN API key
- Use the correct resource ID for your dataset

## 📁 File Locations

```
data/
├── contracts.csv              ← Main dataset (500 contracts)
├── sample_contracts.json      ← JSON example
└── sample_contracts.xml       ← XML example

src/
└── data_loader.py            ← Multi-source loader

frontend/
└── results.json              ← Pipeline output

USAGE_GUIDE.md                ← Detailed guide
DEMO_SCRIPT.md                ← Professor demo
CHANGES_SUMMARY.md            ← What changed
```

## 🎯 Key Features

✅ 5 data sources (Synthetic, CSV, JSON, XML, API)  
✅ Auto column normalization  
✅ API authentication support  
✅ Format flexibility  
✅ Error handling  
✅ Production-ready  

## 🐛 Troubleshooting

**"Module not found"**
→ Activate venv: `source ./venv/Scripts/activate`

**"Missing required columns"**
→ Check column names match required schema

**"API request failed"**
→ Verify API URL and key are correct

**"File not found"**
→ Check file path: `ls data/`

## 📖 Documentation

- **USAGE_GUIDE.md** - Comprehensive examples
- **DEMO_SCRIPT.md** - Step-by-step demo
- **CHANGES_SUMMARY.md** - Implementation details
- **README.md** - Full documentation

## 💡 Demo Tips

1. Start with CSV (fastest)
2. Show JSON/XML samples
3. Explain API integration
4. Emphasize production-ready
5. Show dashboard results

## ⏱️ Demo Timeline

| Step | Time | Command |
|------|------|---------|
| Show options | 1 min | List 5 sources |
| Run pipeline | 1 min | `--source csv` |
| View dashboard | 3 min | Open localhost:8080 |
| Show formats | 2 min | cat sample files |
| Explain API | 2 min | Show API command |

**Total: ~10 minutes**
