# Data Directory

This directory contains data files for the procurement anomaly detection system.

## Files

### Main Dataset
- **`contracts.csv`** (500 rows)
  - Generated synthetic procurement contracts
  - Contains 450 normal + 50 anomalous records
  - Used by default when running: `python run_pipeline.py --source csv`

### Sample Files (for testing different formats)
- **`sample_contracts.json`** - Example JSON format (50 records)
- **`sample_contracts.xml`** - Example XML format (50 records)

**Note:** The sample files contain 50 records which is the minimum for the ML models to work. For better results, use `contracts.csv` (500 records) or generate synthetic data with more contracts.

### Generator Script
- **`generate_data.py`** - Synthetic data generator
  - Run: `python data/generate_data.py` to generate new contracts.csv
  - **Generates different data each time** using current timestamp as seed
  - Creates 500 contracts (450 normal + 50 anomalous)

## Data Schema

All data files must contain these 6 columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| contract_id | String | Unique identifier | "CTR-0042" |
| vendor_name | String | Vendor/supplier name | "Tata Consulting Services" |
| dept | String | Department/ministry | "Ministry of Defence" |
| amount | Number | Contract value (₹) | 12345678.90 |
| award_date | Date | Award date (YYYY-MM-DD) | "2023-06-15" |
| description | String | Tender description | "Supply of network equipment..." |

## Adding Your Own Data

### CSV Format
```csv
contract_id,vendor_name,dept,amount,award_date,description
CTR-001,ABC Corp,Ministry of IT,5000000,2024-01-15,Supply of network equipment
```

### JSON Format
```json
{
  "records": [
    {
      "contract_id": "CTR-001",
      "vendor_name": "ABC Corp",
      "dept": "Ministry of IT",
      "amount": 5000000,
      "award_date": "2024-01-15",
      "description": "Supply of network equipment"
    }
  ]
}
```

### XML Format
```xml
<?xml version="1.0" encoding="UTF-8"?>
<contracts>
  <contract>
    <contract_id>CTR-001</contract_id>
    <vendor_name>ABC Corp</vendor_name>
    <dept>Ministry of IT</dept>
    <amount>5000000</amount>
    <award_date>2024-01-15</award_date>
    <description>Supply of network equipment</description>
  </contract>
</contracts>
```

## Column Name Flexibility

The system automatically normalizes these variations:

- **contract_id**: id, contract_number, tender_id
- **vendor_name**: vendor, supplier, contractor, company
- **dept**: department, ministry, agency
- **amount**: value, contract_value, price, cost
- **award_date**: date, contract_date, award
- **description**: desc, title, tender_description, item

## Usage

```bash
# Use main dataset
python run_pipeline.py --source csv --filepath data/contracts.csv

# Use JSON sample
python run_pipeline.py --source json --filepath data/sample_contracts.json

# Use XML sample
python run_pipeline.py --source xml --filepath data/sample_contracts.xml

# Generate fresh synthetic data
python run_pipeline.py --source synthetic
```

See `USAGE_GUIDE.md` in the root directory for more examples.
