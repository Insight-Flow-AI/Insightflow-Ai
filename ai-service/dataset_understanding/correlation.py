import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def calculate_correlations(df: pd.DataFrame) -> dict:
    """
    Calculates Pearson correlation matrix and extracts significant relationships.
    """
    corr_report = {
        "strong_positive": [],
        "strong_negative": [],
        "matrix": {}
    }
    
    numeric_df = df.select_dtypes(include=[np.number])
    
    if numeric_df.empty or len(numeric_df.columns) < 2:
        return corr_report
        
    try:
        # If > 50 columns, we might limit this, but let's do full for now
        # using pandas .corr()
        corr_matrix = numeric_df.corr(method='pearson')
        
        # Convert to dictionary for matrix representation (lightweight)
        # We round to 3 decimals to save space
        corr_report["matrix"] = corr_matrix.round(3).to_dict()
        
        # Extract upper triangle to avoid duplicates
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        
        # Find strong correlations
        for col1 in upper.columns:
            for col2 in upper.index:
                val = upper.loc[col2, col1]
                if pd.notnull(val):
                    if val >= 0.7:
                        corr_report["strong_positive"].append({"feature_1": col2, "feature_2": col1, "score": round(val, 3)})
                    elif val <= -0.7:
                        corr_report["strong_negative"].append({"feature_1": col2, "feature_2": col1, "score": round(val, 3)})
                        
        logger.info(f"Correlation analysis complete. Found {len(corr_report['strong_positive'])} strong pos, {len(corr_report['strong_negative'])} strong neg.")
        return corr_report
    except Exception as e:
        logger.error(f"Failed to calculate correlations: {e}")
        return {"strong_positive": [], "strong_negative": [], "matrix": {}}
