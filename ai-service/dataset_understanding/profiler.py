import pandas as pd
import logging

logger = logging.getLogger(__name__)

def generate_profile(df: pd.DataFrame, target_col: str = None) -> dict:
    """
    Generates a high-level profile of the dataset's shape and feature types.
    """
    try:
        rows, cols = df.shape
        memory_usage_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        
        feature_types = {
            "numeric": int((df.dtypes == 'float64').sum() + (df.dtypes == 'int64').sum() + (df.dtypes == 'float32').sum() + (df.dtypes == 'int32').sum()),
            "boolean": int((df.dtypes == 'bool').sum()),
            "object": int((df.dtypes == 'object').sum()),
            "datetime": int((df.dtypes == 'datetime64[ns]').sum())
        }
        
        # In a fully engineered dataset, object/datetime should be 0, but we count them just in case.
        
        unique_counts = {col: int(df[col].nunique()) for col in df.columns}
        
        profile = {
            "rows": rows,
            "columns": cols,
            "memory_usage_mb": round(memory_usage_mb, 2),
            "feature_types": feature_types,
            "target_column": target_col,
            "unique_counts": unique_counts
        }
        
        logger.info(f"Dataset profile generated: {rows} rows, {cols} cols.")
        return profile
    except Exception as e:
        logger.error(f"Failed to generate profile: {e}")
        return {}
