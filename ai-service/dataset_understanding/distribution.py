import pandas as pd
import numpy as np
from scipy.stats import skew, kurtosis
import logging

logger = logging.getLogger(__name__)

def analyze_distributions(df: pd.DataFrame) -> dict:
    """
    Calculates skewness, kurtosis, and determines the distribution shape.
    """
    dist_report = {}
    
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        return dist_report
        
    try:
        for col in numeric_df.columns:
            # Dropna just in case, though Phase 3 handled it
            clean_series = numeric_df[col].dropna()
            if clean_series.empty or len(clean_series) < 3:
                continue
                
            col_skew = float(skew(clean_series))
            col_kurt = float(kurtosis(clean_series))
            
            # Determine Shape
            shape = "Normal"
            if col_skew > 1.0:
                shape = "Highly Right Skewed"
            elif col_skew > 0.5:
                shape = "Moderately Right Skewed"
            elif col_skew < -1.0:
                shape = "Highly Left Skewed"
            elif col_skew < -0.5:
                shape = "Moderately Left Skewed"
                
            dist_report[col] = {
                "skewness": round(col_skew, 4),
                "kurtosis": round(col_kurt, 4),
                "shape": shape
            }
            
        logger.info("Distribution analysis completed.")
        return dist_report
    except Exception as e:
        logger.error(f"Failed to analyze distributions: {e}")
        return {}
