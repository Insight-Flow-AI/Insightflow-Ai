import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

def select_features(df: pd.DataFrame, target_col: str = None) -> tuple[pd.DataFrame, list]:
    """
    Removes highly correlated features to reduce dimensionality and multicollinearity.
    Strictly protects the target column.
    """
    dropped_cols = []
    
    # 1. Isolate the feature matrix (only numeric columns)
    # At this stage, everything should be numeric (scaled, encoded), but we double-check.
    numeric_df = df.select_dtypes(include=[np.number])
    
    if target_col and target_col in numeric_df.columns:
        feature_matrix = numeric_df.drop(columns=[target_col])
    else:
        feature_matrix = numeric_df
        
    if feature_matrix.empty:
        return df, dropped_cols
        
    try:
        # Calculate correlation matrix
        corr_matrix = feature_matrix.corr().abs()
        
        # Select upper triangle of correlation matrix
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        
        # Find features with correlation greater than 0.99
        to_drop = [column for column in upper.columns if any(upper[column] > 0.99)]
        
        if to_drop:
            df.drop(columns=to_drop, inplace=True)
            dropped_cols.extend(to_drop)
            logger.info(f"Dropped {len(to_drop)} highly correlated features: {to_drop}")
            
    except Exception as e:
        logger.error(f"Correlation feature selection failed: {e}")
        
    return df, dropped_cols
