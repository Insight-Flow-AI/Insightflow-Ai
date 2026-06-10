import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def calculate_descriptive_statistics(df: pd.DataFrame) -> dict:
    """
    Calculates Mean, Median, Mode, Min, Max, Variance, Standard Deviation, Range, and Percentiles
    for every numeric feature in the dataset.
    """
    stats_report = {}
    
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty:
        logger.warning("No numeric columns found for descriptive statistics.")
        return stats_report
        
    try:
        # Vectorized calculation for speed
        summary = numeric_df.describe(percentiles=[.25, .50, .75]).T
        variances = numeric_df.var()
        modes = numeric_df.mode().iloc[0] if not numeric_df.mode().empty else pd.Series(index=numeric_df.columns, dtype=float)
        
        for col in numeric_df.columns:
            stats_report[col] = {
                "mean": float(summary.loc[col, "mean"]) if pd.notnull(summary.loc[col, "mean"]) else None,
                "median": float(summary.loc[col, "50%"]) if pd.notnull(summary.loc[col, "50%"]) else None,
                "mode": float(modes[col]) if pd.notnull(modes[col]) else None,
                "min": float(summary.loc[col, "min"]) if pd.notnull(summary.loc[col, "min"]) else None,
                "max": float(summary.loc[col, "max"]) if pd.notnull(summary.loc[col, "max"]) else None,
                "variance": float(variances[col]) if pd.notnull(variances[col]) else None,
                "std_dev": float(summary.loc[col, "std"]) if pd.notnull(summary.loc[col, "std"]) else None,
                "range": float(summary.loc[col, "max"] - summary.loc[col, "min"]) if pd.notnull(summary.loc[col, "max"]) and pd.notnull(summary.loc[col, "min"]) else None,
                "percentiles": {
                    "25th": float(summary.loc[col, "25%"]) if pd.notnull(summary.loc[col, "25%"]) else None,
                    "50th": float(summary.loc[col, "50%"]) if pd.notnull(summary.loc[col, "50%"]) else None,
                    "75th": float(summary.loc[col, "75%"]) if pd.notnull(summary.loc[col, "75%"]) else None
                }
            }
            
        logger.info("Descriptive statistics calculated successfully.")
        return stats_report
    except Exception as e:
        logger.error(f"Failed to calculate descriptive statistics: {e}")
        return {}
