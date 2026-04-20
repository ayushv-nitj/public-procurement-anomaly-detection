"""
Synthetic Data Generator for Public Procurement Anomaly Detection
Generates ~500 realistic procurement contract records with injected anomalies.
"""

import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

# --- Configuration ---
NUM_RECORDS = 500
ANOMALY_FRACTION = 0.10  # ~10% anomalous records

# --- Vendor names (mix of normal + suspicious duplicates) ---
NORMAL_VENDORS = [
    "Tata Consulting Services", "Infosys Ltd", "Wipro Technologies",
    "HCL Technologies", "Tech Mahindra", "L&T Infotech",
    "Reliance Jio Infocomm", "Bharat Electronics Ltd", "Hindustan Aeronautics Ltd",
    "ONGC Videsh", "NTPC Limited", "Power Grid Corp",
    "Godrej & Boyce", "Larsen & Toubro", "Siemens India",
    "ABB India Ltd", "Schneider Electric India", "Thermax Ltd",
    "Kirloskar Brothers", "Cummins India", "Ashok Leyland",
    "Mahindra Defence Systems", "BEL Optronic Devices", "Garden Reach Shipbuilders",
    "Bharat Dynamics Ltd", "Mazagon Dock Shipbuilders", "Cochin Shipyard Ltd",
    "Rail Vikas Nigam", "IRCON International", "RITES Ltd",
    "NBCC India Ltd", "Engineers India Ltd", "WAPCOS Ltd",
    "MECON Ltd", "BEML Ltd", "Central Electronics Ltd",
    "ITI Ltd", "ECIL Hyderabad", "Rolta India",
    "Zensar Technologies", "Mphasis Ltd", "Cyient Ltd"
]

# Suspicious vendors (slight misspellings — for fuzzy matching detection)
SUSPICIOUS_VENDORS = [
    "Tata Consulitng Services", "Infossys Ltd", "Wiproo Technologies",
    "BEL Optronics Devices", "Bharatt Electronics Ltd"
]

# --- Departments ---
DEPARTMENTS = [
    "Ministry of Defence", "Ministry of Railways", "Ministry of Health",
    "Ministry of Education", "Ministry of Power", "Ministry of IT",
    "Ministry of Urban Development", "Ministry of Agriculture",
    "Ministry of Finance", "Ministry of Home Affairs",
    "Department of Space", "Department of Atomic Energy"
]

# --- Tender description templates ---
NORMAL_DESCRIPTIONS = [
    "Supply of {item} for {dept} under annual maintenance contract",
    "Procurement of {item} for government offices in {city}",
    "Installation and commissioning of {item} at {dept} facilities",
    "Annual maintenance contract for {item} across {dept} offices",
    "Consultancy services for {item} implementation in {dept}",
    "Design, supply, and installation of {item} for {dept}",
    "Turnkey project for {item} modernization at {dept}",
    "Rate contract for supply of {item} to {dept} for FY 2024-25",
    "Empanelment of vendors for {item} supply to {dept}",
    "Comprehensive maintenance of {item} systems at {dept} locations"
]

ITEMS = [
    "network equipment", "server infrastructure", "security systems",
    "office furniture", "medical equipment", "railway signalling systems",
    "power transformers", "solar panels", "IT hardware",
    "surveillance cameras", "communication devices", "laboratory equipment",
    "air conditioning units", "fire safety systems", "water treatment plants",
    "electrical substations", "road construction materials", "bridge components",
    "satellite communication equipment", "radar systems"
]

CITIES = [
    "New Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad",
    "Kolkata", "Pune", "Ahmedabad", "Lucknow", "Jaipur"
]

# Suspicious description templates (near-duplicates for NLP detection)
SUSPICIOUS_DESCRIPTIONS = [
    "Supply of misc items for general use in department offices",
    "Procurement of sundry materials for miscellaneous departmental needs",
    "Supply of miscellaneous items for general departmental use",
    "General supply of sundry materials for office requirements",
    "Miscellaneous procurement of items for departmental offices"
]


def generate_normal_record(contract_id, start_date):
    """Generate a single normal procurement record."""
    vendor = random.choice(NORMAL_VENDORS)
    dept = random.choice(DEPARTMENTS)
    item = random.choice(ITEMS)
    city = random.choice(CITIES)

    # Normal amounts: ₹1 lakh to ₹50 crore (log-normal distribution)
    amount = round(np.random.lognormal(mean=14, sigma=1.5), 2)
    amount = max(100000, min(amount, 500000000))  # Clamp to 1L - 50Cr

    # Random date within 2 years
    days_offset = random.randint(0, 730)
    award_date = start_date + timedelta(days=days_offset)

    # Generate description
    template = random.choice(NORMAL_DESCRIPTIONS)
    description = template.format(item=item, dept=dept.split("of ")[-1], city=city)

    return {
        "contract_id": f"CTR-{contract_id:04d}",
        "vendor_name": vendor,
        "dept": dept,
        "amount": amount,
        "award_date": award_date.strftime("%Y-%m-%d"),
        "description": description
    }


def generate_anomalous_record(contract_id, start_date):
    """Generate a suspicious/anomalous procurement record."""
    anomaly_type = random.choice(["inflated", "suspicious_vendor", "duplicate_desc", "rapid_fire"])

    if anomaly_type == "inflated":
        # Abnormally high amount for a routine item
        record = generate_normal_record(contract_id, start_date)
        record["amount"] = round(np.random.uniform(600000000, 2000000000), 2)  # ₹60Cr to ₹200Cr
        return record

    elif anomaly_type == "suspicious_vendor":
        # Vendor name is a near-duplicate (typo variant)
        record = generate_normal_record(contract_id, start_date)
        record["vendor_name"] = random.choice(SUSPICIOUS_VENDORS)
        record["amount"] = round(np.random.uniform(50000000, 800000000), 2)
        return record

    elif anomaly_type == "duplicate_desc":
        # Suspicious near-duplicate description
        record = generate_normal_record(contract_id, start_date)
        record["description"] = random.choice(SUSPICIOUS_DESCRIPTIONS)
        record["amount"] = round(np.random.uniform(10000000, 300000000), 2)
        return record

    elif anomaly_type == "rapid_fire":
        # Multiple contracts awarded very close together (same vendor)
        vendor = random.choice(NORMAL_VENDORS[:10])  # Pick from top vendors
        dept = random.choice(DEPARTMENTS[:4])
        base_date = start_date + timedelta(days=random.randint(0, 700))

        record = {
            "contract_id": f"CTR-{contract_id:04d}",
            "vendor_name": vendor,
            "dept": dept,
            "amount": round(np.random.uniform(50000000, 500000000), 2),
            "award_date": (base_date + timedelta(days=random.randint(0, 3))).strftime("%Y-%m-%d"),
            "description": random.choice(SUSPICIOUS_DESCRIPTIONS)
        }
        return record


def generate_dataset():
    """Generate the full synthetic dataset."""
    start_date = datetime(2022, 1, 1)
    records = []

    num_anomalies = int(NUM_RECORDS * ANOMALY_FRACTION)
    num_normal = NUM_RECORDS - num_anomalies

    # Generate normal records
    for i in range(num_normal):
        records.append(generate_normal_record(i + 1, start_date))

    # Generate anomalous records
    for i in range(num_anomalies):
        records.append(generate_anomalous_record(num_normal + i + 1, start_date))

    # Shuffle
    random.shuffle(records)

    # Re-assign contract IDs after shuffle
    for idx, record in enumerate(records):
        record["contract_id"] = f"CTR-{idx + 1:04d}"

    df = pd.DataFrame(records)

    # Save
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(output_dir, "contracts.csv")
    df.to_csv(output_path, index=False)

    print(f"Dataset generated: {output_path} ({len(df)} rows)")
    print(f"  Normal records:    {num_normal}")
    print(f"  Anomalous records: {num_anomalies}")
    print(f"  Columns: {list(df.columns)}")

    return df


if __name__ == "__main__":
    generate_dataset()
