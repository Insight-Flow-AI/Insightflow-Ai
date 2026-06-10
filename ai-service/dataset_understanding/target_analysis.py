import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def analyze_target(df: pd.DataFrame, target_col: str) -> dict:
    """
    Analyzes the target variable for class imbalance (classification)
    or distribution spread (regression).
    """
    target_report = {
        "is_imbalanced": False,
        "type": "UNKNOWN"
    }
    
    if not target_col or target_col not in df.columns:
        logger.info("No target column provided or found for target analysis.")
        return target_report
        
    try:
        target_series = df[target_col].dropna()
        unique_vals = target_series.nunique()
        
        # Heuristic: If unique values < 10 or dtype is object, it's Classification
        if unique_vals < 10 or not pd.api.types.is_numeric_dtype(target_series):
            target_report["type"] = "CLASSIFICATION"
            counts = target_series.value_counts(normalize=True).to_dict()
            target_report["class_distribution"] = {str(k): round(v, 4) for k, v in counts.items()}
            
            # Check for imbalance
            min_class_ratio = min(counts.values())
            if min_class_ratio < 0.20:
                target_report["is_imbalanced"] = True
                target_report["minority_class_ratio"] = round(min_class_ratio, 4)
                
        else:
            target_report["type"] = "REGRESSION"
            target_report["variance"] = float(target_series.var())
            target_report["skewness"] = float(target_series.skew())
            
            # Check for highly skewed regression target
            if abs(target_report["skewness"]) > 2.0:
                target_report["is_imbalanced"] = True # We use this flag broadly for 'problematic' target
                
        logger.info(f"Target analysis complete. Type: {target_report['type']}, Imbalanced: {target_report['is_imbalanced']}")
        return target_report
    except Exception as e:
        logger.error(f"Failed to analyze target: {e}")
        return target_report
