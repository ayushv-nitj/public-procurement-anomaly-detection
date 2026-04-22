"""
Feature Engineering Module
Transforms raw contract data into ML-ready features.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler


def compute_vendor_frequency(df):
    """Count how many contracts each vendor has been awarded."""
    vendor_counts = df["vendor_name"].value_counts()
    df["vendor_freq"] = df["vendor_name"].map(vendor_counts)
    return df


def compute_amount_zscore(df):
    """Compute z-score of contract amount within each department."""
    df["amount_zscore"] = df.groupby("dept")["amount"].transform(
        lambda x: (x - x.mean()) / (x.std() + 1e-8)
    )
    return df


def compute_days_since_last(df):
    """
    For each vendor, compute days since their previous contract.
    Low values indicate rapid-fire awarding (suspicious).
    """
    df["award_date_dt"] = pd.to_datetime(df["award_date"])
    df = df.sort_values(["vendor_name", "award_date_dt"])
    df["days_since_last"] = df.groupby("vendor_name")["award_date_dt"].diff().dt.days
    df["days_since_last"] = df["days_since_last"].fillna(365)  # Default for first contract
    return df


def compute_amount_per_dept_ratio(df):
    """Ratio of contract amount to department median — flags outliers."""
    dept_median = df.groupby("dept")["amount"].transform("median")
    df["amount_dept_ratio"] = df["amount"] / (dept_median + 1e-8)
    return df


def encode_categoricals(df):
    """Label-encode vendor_name and dept for ML models."""
    le_vendor = LabelEncoder()
    le_dept = LabelEncoder()
    df["vendor_encoded"] = le_vendor.fit_transform(df["vendor_name"])
    df["dept_encoded"] = le_dept.fit_transform(df["dept"])
    return df, le_vendor, le_dept


def build_feature_matrix(df):
    """
    Full feature engineering pipeline.
    Returns: df with new columns, feature_matrix (numpy array), feature_names (list)
    """
    # Compute all features
    df = compute_vendor_frequency(df)
    df = compute_amount_zscore(df)
    df = compute_days_since_last(df)
    df = compute_amount_per_dept_ratio(df)
    df, le_vendor, le_dept = encode_categoricals(df)

    # Define feature columns for ML
    feature_cols = [
        "amount",
        "vendor_freq",
        "amount_zscore",
        "days_since_last",
        "amount_dept_ratio",
        "vendor_encoded",
        "dept_encoded"
    ]

    # Fill any NaN values before scaling
    # NaN can occur in small datasets (e.g., amount_zscore when dept has only 1 contract)
    df[feature_cols] = df[feature_cols].fillna(0)

    # Scale features
    scaler = StandardScaler()
    feature_matrix = scaler.fit_transform(df[feature_cols].values)

    return df, feature_matrix, feature_cols, scaler
