"""
Data Validation and Cleaning Module
Handles real-world data quality issues
"""
import pandas as pd
import numpy as np
from datetime import datetime
import re
from fuzzywuzzy import fuzz, process
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """
    Validates and cleans procurement contract data
    Handles missing values, wrong formats, inconsistent naming
    """
    
    def __init__(self):
        self.required_columns = [
            'contract_id', 'vendor_name', 'dept', 
            'amount', 'award_date', 'description'
        ]
        
        # Common column name variations (schema mapping)
        self.column_mapping = {
            # Vendor variations
            'vendor': 'vendor_name',
            'supplier': 'vendor_name',
            'contractor': 'vendor_name',
            'company': 'vendor_name',
            'vendor_id': 'vendor_name',
            
            # Department variations
            'department': 'dept',
            'ministry': 'dept',
            'organization': 'dept',
            'org': 'dept',
            'dept_name': 'dept',
            
            # Amount variations
            'value': 'amount',
            'contract_value': 'amount',
            'price': 'amount',
            'cost': 'amount',
            'value_inr': 'amount',
            'amount_inr': 'amount',
            
            # Date variations
            'date': 'award_date',
            'contract_date': 'award_date',
            'award': 'award_date',
            'signed_date': 'award_date',
            
            # Description variations
            'desc': 'description',
            'details': 'description',
            'tender_description': 'description',
            'item': 'description',
            'subject': 'description',
            
            # Contract ID variations
            'id': 'contract_id',
            'contract_no': 'contract_id',
            'contract_number': 'contract_id',
            'reference': 'contract_id',
            'ref_no': 'contract_id'
        }
        
        # Vendor name normalization cache
        self.vendor_cache = {}
        
    def validate_and_clean(self, df):
        """
        Main validation and cleaning pipeline
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame, validation report
        """
        logger.info(f"Starting validation for {len(df)} records")
        
        report = {
            'original_rows': len(df),
            'issues_found': [],
            'rows_dropped': 0,
            'rows_cleaned': 0
        }
        
        # Step 1: Map columns to standard schema
        df, mapping_report = self._map_columns(df)
        report['column_mapping'] = mapping_report
        
        # Step 2: Check required columns
        missing_cols = set(self.required_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Step 3: Handle missing values
        df, null_report = self._handle_nulls(df)
        report['null_handling'] = null_report
        report['rows_dropped'] += null_report['rows_dropped']
        
        # Step 4: Clean and standardize data types
        df, type_report = self._standardize_types(df)
        report['type_standardization'] = type_report
        
        # Step 5: Normalize vendor names
        df, vendor_report = self._normalize_vendors(df)
        report['vendor_normalization'] = vendor_report
        
        # Step 6: Clean text fields
        df = self._clean_text_fields(df)
        
        # Step 7: Validate data ranges
        df, range_report = self._validate_ranges(df)
        report['range_validation'] = range_report
        report['rows_dropped'] += range_report['rows_dropped']
        
        # Step 8: Remove duplicates
        df, dup_report = self._remove_duplicates(df)
        report['duplicate_removal'] = dup_report
        report['rows_dropped'] += dup_report['rows_dropped']
        
        report['final_rows'] = len(df)
        report['data_quality_score'] = self._calculate_quality_score(report)
        
        logger.info(f"Validation complete. {report['final_rows']} records remaining")
        logger.info(f"Data quality score: {report['data_quality_score']:.2f}/100")
        
        return df, report
    
    def _map_columns(self, df):
        """Map column names to standard schema"""
        report = {'mapped': {}, 'unmapped': []}
        
        # Convert all column names to lowercase for matching
        df.columns = df.columns.str.lower().str.strip()
        
        # Apply mapping
        renamed = {}
        for col in df.columns:
            if col in self.column_mapping:
                renamed[col] = self.column_mapping[col]
                report['mapped'][col] = self.column_mapping[col]
        
        if renamed:
            df = df.rename(columns=renamed)
            logger.info(f"Mapped {len(renamed)} columns: {renamed}")
        
        # Check for unmapped columns
        for col in df.columns:
            if col not in self.required_columns:
                report['unmapped'].append(col)
        
        return df, report
    
    def _handle_nulls(self, df):
        """Handle missing values"""
        report = {
            'null_counts': {},
            'rows_dropped': 0,
            'values_imputed': 0
        }
        
        # Count nulls per column
        for col in self.required_columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                report['null_counts'][col] = null_count
        
        # Critical columns: drop rows if null
        critical_cols = ['contract_id', 'vendor_name', 'amount', 'award_date']
        before_len = len(df)
        df = df.dropna(subset=critical_cols)
        report['rows_dropped'] = before_len - len(df)
        
        # Non-critical columns: impute
        if df['dept'].isnull().any():
            df['dept'] = df['dept'].fillna('Unknown')
            report['values_imputed'] += df['dept'].isnull().sum()
        
        if df['description'].isnull().any():
            df['description'] = df['description'].fillna('No description provided')
            report['values_imputed'] += df['description'].isnull().sum()
        
        return df, report
    
    def _standardize_types(self, df):
        """Standardize data types and formats"""
        report = {'conversions': [], 'errors': []}
        
        # 1. Contract ID: Convert to string
        try:
            df['contract_id'] = df['contract_id'].astype(str).str.strip()
            report['conversions'].append('contract_id → string')
        except Exception as e:
            report['errors'].append(f"contract_id conversion failed: {e}")
        
        # 2. Amount: Convert to float
        try:
            # Remove currency symbols and commas
            df['amount'] = df['amount'].astype(str).str.replace('[₹$,]', '', regex=True)
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            # Drop rows with invalid amounts
            df = df.dropna(subset=['amount'])
            report['conversions'].append('amount → float')
        except Exception as e:
            report['errors'].append(f"amount conversion failed: {e}")
        
        # 3. Award Date: Parse dates
        try:
            df['award_date'] = pd.to_datetime(df['award_date'], errors='coerce', 
                                              infer_datetime_format=True)
            # Drop rows with invalid dates
            df = df.dropna(subset=['award_date'])
            # Convert to string format YYYY-MM-DD
            df['award_date'] = df['award_date'].dt.strftime('%Y-%m-%d')
            report['conversions'].append('award_date → datetime → string')
        except Exception as e:
            report['errors'].append(f"award_date conversion failed: {e}")
        
        # 4. Text fields: Convert to string
        for col in ['vendor_name', 'dept', 'description']:
            try:
                df[col] = df[col].astype(str).str.strip()
            except Exception as e:
                report['errors'].append(f"{col} conversion failed: {e}")
        
        return df, report
    
    def _normalize_vendors(self, df):
        """Normalize vendor names using fuzzy matching"""
        report = {
            'unique_before': df['vendor_name'].nunique(),
            'normalized_count': 0
        }
        
        # Get unique vendor names
        unique_vendors = df['vendor_name'].unique()
        
        # Build normalization mapping
        normalized_map = {}
        
        for vendor in unique_vendors:
            # Clean vendor name
            cleaned = self._clean_vendor_name(vendor)
            
            # Check cache
            if cleaned in self.vendor_cache:
                normalized_map[vendor] = self.vendor_cache[cleaned]
                continue
            
            # Find similar vendors using fuzzy matching
            matches = process.extract(cleaned, unique_vendors, 
                                     scorer=fuzz.token_sort_ratio, limit=5)
            
            # If high similarity found, use the most common one
            similar = [m[0] for m in matches if m[1] > 85]
            if len(similar) > 1:
                # Use the shortest name (usually the canonical one)
                canonical = min(similar, key=len)
                normalized_map[vendor] = canonical
                self.vendor_cache[cleaned] = canonical
                report['normalized_count'] += 1
            else:
                normalized_map[vendor] = vendor
                self.vendor_cache[cleaned] = vendor
        
        # Apply normalization
        df['vendor_name'] = df['vendor_name'].map(normalized_map)
        
        report['unique_after'] = df['vendor_name'].nunique()
        report['reduction'] = report['unique_before'] - report['unique_after']
        
        logger.info(f"Vendor normalization: {report['unique_before']} → {report['unique_after']} "
                   f"({report['reduction']} merged)")
        
        return df, report
    
    def _clean_vendor_name(self, name):
        """Clean vendor name for comparison"""
        # Convert to lowercase
        name = name.lower()
        # Remove common suffixes
        suffixes = ['ltd', 'limited', 'pvt', 'private', 'inc', 'corp', 
                   'corporation', 'company', 'co', 'llc', 'llp']
        for suffix in suffixes:
            name = re.sub(rf'\b{suffix}\b\.?', '', name)
        # Remove special characters
        name = re.sub(r'[^\w\s]', '', name)
        # Remove extra spaces
        name = ' '.join(name.split())
        return name.strip()
    
    def _clean_text_fields(self, df):
        """Clean text fields"""
        # Vendor name
        df['vendor_name'] = df['vendor_name'].str.strip()
        df['vendor_name'] = df['vendor_name'].str.title()  # Title case
        
        # Department
        df['dept'] = df['dept'].str.strip()
        df['dept'] = df['dept'].str.title()
        
        # Description
        df['description'] = df['description'].str.strip()
        df['description'] = df['description'].str.lower()  # Lowercase for NLP
        
        return df
    
    def _validate_ranges(self, df):
        """Validate data ranges"""
        report = {'rows_dropped': 0, 'issues': []}
        
        before_len = len(df)
        
        # Amount: Must be positive
        invalid_amount = df['amount'] <= 0
        if invalid_amount.any():
            report['issues'].append(f"{invalid_amount.sum()} contracts with amount <= 0")
            df = df[~invalid_amount]
        
        # Amount: Reasonable upper limit (e.g., 1000 Crore)
        max_amount = 10_000_000_000  # 1000 Cr
        too_high = df['amount'] > max_amount
        if too_high.any():
            report['issues'].append(f"{too_high.sum()} contracts with amount > {max_amount}")
            df = df[~too_high]
        
        # Date: Not in future
        df['award_date_dt'] = pd.to_datetime(df['award_date'])
        future_dates = df['award_date_dt'] > datetime.now()
        if future_dates.any():
            report['issues'].append(f"{future_dates.sum()} contracts with future dates")
            df = df[~future_dates]
        df = df.drop('award_date_dt', axis=1)
        
        # Date: Not too old (e.g., before 2000)
        df['award_date_dt'] = pd.to_datetime(df['award_date'])
        too_old = df['award_date_dt'] < pd.Timestamp('2000-01-01')
        if too_old.any():
            report['issues'].append(f"{too_old.sum()} contracts before 2000")
            df = df[~too_old]
        df = df.drop('award_date_dt', axis=1)
        
        report['rows_dropped'] = before_len - len(df)
        
        return df, report
    
    def _remove_duplicates(self, df):
        """Remove duplicate records"""
        report = {}
        
        before_len = len(df)
        
        # Exact duplicates
        df = df.drop_duplicates()
        exact_dups = before_len - len(df)
        report['exact_duplicates'] = exact_dups
        
        # Duplicates based on contract_id
        df = df.drop_duplicates(subset=['contract_id'], keep='first')
        id_dups = before_len - exact_dups - len(df)
        report['id_duplicates'] = id_dups
        
        report['rows_dropped'] = exact_dups + id_dups
        
        if report['rows_dropped'] > 0:
            logger.info(f"Removed {report['rows_dropped']} duplicates")
        
        return df, report
    
    def _calculate_quality_score(self, report):
        """Calculate overall data quality score (0-100)"""
        score = 100.0
        
        # Penalize for rows dropped
        if report['original_rows'] > 0:
            drop_rate = report['rows_dropped'] / report['original_rows']
            score -= drop_rate * 30  # Max 30 points penalty
        
        # Penalize for null values
        null_count = sum(report['null_handling']['null_counts'].values())
        if report['original_rows'] > 0:
            null_rate = null_count / (report['original_rows'] * len(self.required_columns))
            score -= null_rate * 20  # Max 20 points penalty
        
        # Bonus for vendor normalization
        if 'vendor_normalization' in report:
            if report['vendor_normalization']['reduction'] > 0:
                score += 5  # Bonus for cleaning
        
        return max(0, min(100, score))


def validate_data(df):
    """
    Convenience function to validate and clean data
    
    Args:
        df: Raw DataFrame
        
    Returns:
        Cleaned DataFrame, validation report
    """
    validator = DataValidator()
    return validator.validate_and_clean(df)
