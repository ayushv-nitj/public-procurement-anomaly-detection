"""
Data Loader Module
Supports multiple data sources: synthetic generation, API, CSV, XML, JSON
"""

import pandas as pd
import requests
import json
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any
import os


def load_from_synthetic() -> pd.DataFrame:
    """Generate synthetic data using existing generator."""
    from data.generate_data import generate_dataset
    return generate_dataset()


def load_from_csv(filepath: str) -> pd.DataFrame:
    """Load data from CSV file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    return pd.read_csv(filepath)


def load_from_json(filepath: str) -> pd.DataFrame:
    """Load data from JSON file (expects array of objects or records format)."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"JSON file not found: {filepath}")
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Handle both array format and {records: [...]} format
    if isinstance(data, dict) and 'records' in data:
        data = data['records']
    
    return pd.DataFrame(data)


def load_from_xml(filepath: str) -> pd.DataFrame:
    """Load data from XML file (expects <contracts><contract>...</contract></contracts> structure)."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"XML file not found: {filepath}")
    
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    records = []
    for contract in root.findall('contract'):
        record = {}
        for child in contract:
            record[child.tag] = child.text
        records.append(record)
    
    return pd.DataFrame(records)


def load_from_api(api_url: str, api_key: Optional[str] = None, 
                  params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Load data from API endpoint.
    
    Args:
        api_url: Full API endpoint URL
        api_key: Optional API key for authentication
        params: Optional query parameters (format, offset, limit, etc.)
    
    Returns:
        DataFrame with procurement data
    """
    headers = {}
    if api_key:
        headers['api_key'] = api_key
    
    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        # Try to parse as JSON
        data = response.json()
        
        # Handle different API response formats
        if isinstance(data, dict):
            # Check for common wrapper keys
            for key in ['records', 'data', 'results', 'contracts']:
                if key in data:
                    data = data[key]
                    break
        
        df = pd.DataFrame(data)
        return df
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            raise Exception(
                f"API request failed with 400 Bad Request.\n"
                f"Possible reasons:\n"
                f"  - Invalid or expired API key\n"
                f"  - Invalid resource ID\n"
                f"  - Missing required parameters\n"
                f"URL: {e.response.url}\n"
                f"Response: {e.response.text[:200]}"
            )
        elif e.response.status_code == 403:
            raise Exception(
                f"API request failed with 403 Forbidden.\n"
                f"Your API key may not have access to this resource.\n"
                f"Please request access from the data officer."
            )
        else:
            raise Exception(f"API request failed: {str(e)}")
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("API response is not valid JSON")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to match expected schema.
    Maps common variations to standard names.
    """
    column_mapping = {
        # Contract ID variations
        'id': 'contract_id',
        'contract_number': 'contract_id',
        'tender_id': 'contract_id',
        
        # Vendor variations
        'vendor': 'vendor_name',
        'supplier': 'vendor_name',
        'contractor': 'vendor_name',
        'company': 'vendor_name',
        
        # Department variations
        'department': 'dept',
        'ministry': 'dept',
        'agency': 'dept',
        
        # Amount variations
        'value': 'amount',
        'contract_value': 'amount',
        'price': 'amount',
        'cost': 'amount',
        
        # Date variations
        'date': 'award_date',
        'contract_date': 'award_date',
        'award': 'award_date',
        
        # Description variations
        'desc': 'description',
        'title': 'description',
        'tender_description': 'description',
        'item': 'description'
    }
    
    # Rename columns (case-insensitive)
    df.columns = df.columns.str.lower().str.strip()
    
    # Apply mapping only for columns that exist and target doesn't already exist
    rename_dict = {}
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            rename_dict[old_col] = new_col
    
    df = df.rename(columns=rename_dict)
    
    # Ensure required columns exist
    required_cols = ['contract_id', 'vendor_name', 'dept', 'amount', 'award_date', 'description']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        raise ValueError(f"Missing required columns after normalization: {missing_cols}")
    
    # Convert amount to numeric (handle both object and string types)
    df['amount'] = pd.to_numeric(df['amount'].astype(str).str.replace(',', '').str.replace('₹', '').str.strip(), errors='coerce')
    
    # Ensure date format
    try:
        df['award_date'] = pd.to_datetime(df['award_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    except Exception:
        # If date parsing fails, try to keep as string
        df['award_date'] = df['award_date'].astype(str)
    
    return df[required_cols]


def load_data(source: str = 'synthetic', **kwargs) -> pd.DataFrame:
    """
    Universal data loader supporting multiple sources.
    
    Args:
        source: Data source type ('synthetic', 'csv', 'json', 'xml', 'api')
        **kwargs: Source-specific parameters
            - For 'csv', 'json', 'xml': filepath='path/to/file'
            - For 'api': api_url='...', api_key='...', params={...}
    
    Returns:
        Normalized DataFrame with standard schema
    """
    print(f"Loading data from source: {source}")
    
    if source == 'synthetic':
        df = load_from_synthetic()
    elif source == 'csv':
        df = load_from_csv(kwargs.get('filepath', 'data/contracts.csv'))
    elif source == 'json':
        df = load_from_json(kwargs['filepath'])
    elif source == 'xml':
        df = load_from_xml(kwargs['filepath'])
    elif source == 'api':
        df = load_from_api(
            api_url=kwargs['api_url'],
            api_key=kwargs.get('api_key'),
            params=kwargs.get('params')
        )
    else:
        raise ValueError(f"Unknown data source: {source}. Supported: synthetic, csv, json, xml, api")
    
    # Normalize columns if not from synthetic (synthetic already has correct schema)
    if source != 'synthetic':
        df = normalize_columns(df)
    
    print(f"Loaded {len(df)} contracts")
    return df
