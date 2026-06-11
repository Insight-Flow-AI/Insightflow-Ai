import pandas as pd
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

def scale_numerical_features(df: pd.DataFrame, num_cols: list, target_col: str = None) -> tuple[pd.DataFrame, dict]:
    """
    Applies StandardScaler to numerical features.
    Strictly ignores the target column to prevent data leakage.
    Returns the scaled DataFrame and scaler metadata.
    """
    scaler_metadata = {}
    
    # Filter columns to scale (must be in df and NOT the target)
    cols_to_scale = [col for col in num_cols if col in df.columns and col != target_col]
    
    if not cols_to_scale:
        logger.info("No numerical columns to scale.")
        return df, scaler_metadata
        
    try:
        scaler = StandardScaler()
        df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
        
        # We save mean and scale (std) for later use in predictions (Phase 14)
        scaler_metadata = {
            'type': 'StandardScaler',
            'features': cols_to_scale,
            'means': scaler.mean_.tolist(),
            'scales': scaler.scale_.tolist()
        }
        
        logger.info(f"Successfully scaled {len(cols_to_scale)} numerical columns.")
        
    except Exception as e:
        logger.error(f"Scaling failed: {e}")
        
    return df, scaler_metadata
