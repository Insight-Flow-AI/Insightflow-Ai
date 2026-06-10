import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def generate_visualization_metadata(df: pd.DataFrame) -> dict:
    """
    Generates lightweight JSON payload representing histogram bins 
    for frontend rendering (avoids sending heavy images).
    """
    viz_data = {
        "histograms": []
    }
    
    numeric_df = df.select_dtypes(include=[np.number])
    
    # Generate histograms for max 10 numeric features to save DB space
    for col in numeric_df.columns[:10]:
        try:
            clean_series = numeric_df[col].dropna()
            if clean_series.empty:
                continue
                
            # Create 10 bins
            counts, bin_edges = np.histogram(clean_series, bins=10)
            
            bins_data = []
            for i in range(len(counts)):
                range_str = f"{round(bin_edges[i], 2)} to {round(bin_edges[i+1], 2)}"
                bins_data.append({
                    "range": range_str,
                    "count": int(counts[i])
                })
                
            viz_data["histograms"].append({
                "column": col,
                "bins": bins_data
            })
        except Exception as e:
            logger.warning(f"Failed to generate viz metadata for {col}: {e}")
            
    logger.info(f"Generated viz metadata for {len(viz_data['histograms'])} histograms.")
    return viz_data
