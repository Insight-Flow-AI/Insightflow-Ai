import pandas as pd
import numpy as np

def analyze_target(df: pd.DataFrame, target_column: str) -> dict:
    if target_column not in df.columns:
        return {"exists": False}

    target_series = df[target_column].dropna()
    unique_vals = target_series.nunique()
    
    # Calculate entropy
    value_counts = target_series.value_counts(normalize=True)
    entropy = -sum(p * np.log2(p) for p in value_counts if p > 0)
    
    # Calculate variance if numeric
    variance = None
    if pd.api.types.is_numeric_dtype(target_series):
        variance = target_series.var()

    datatype = "UNKNOWN"
    if pd.api.types.is_numeric_dtype(target_series):
        datatype = "NUMERIC"
    elif pd.api.types.is_datetime64_any_dtype(target_series):
        datatype = "DATETIME"
    elif pd.api.types.is_bool_dtype(target_series):
        datatype = "BOOLEAN"
    elif target_series.dtype == object:
        datatype = "CATEGORICAL"

    return {
        "exists": True,
        "columnName": target_column,
        "datatype": datatype,
        "uniqueValues": int(unique_vals),
        "missingValues": int(df[target_column].isnull().sum()),
        "entropy": float(entropy),
        "variance": float(variance) if variance is not None else None
    }
