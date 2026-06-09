import pandas as pd
import logging

logger = logging.getLogger(__name__)

def extract_datetime_features(df: pd.DataFrame, datetime_cols: list) -> pd.DataFrame:
    """
    Extracts Day, Month, Year, and Weekend features from datetime columns.
    Drops the original datetime column to ensure numerical purity.
    """
    generated_count = 0
    
    for col in datetime_cols:
        if col not in df.columns:
            continue
            
        try:
            # Coerce to datetime, invalid parsing will be set as NaT
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
            # Extract features
            df[f"{col}_Year"] = df[col].dt.year
            df[f"{col}_Month"] = df[col].dt.month
            df[f"{col}_Day"] = df[col].dt.day
            df[f"{col}_Weekend"] = df[col].dt.dayofweek.apply(lambda x: 1 if pd.notnull(x) and x >= 5 else 0)
            
            # Handle possible NaNs created by 'coerce' using 0 or -1
            df.fillna({
                f"{col}_Year": -1,
                f"{col}_Month": -1,
                f"{col}_Day": -1
            }, inplace=True)
            
            # Drop the original string/datetime column
            df.drop(columns=[col], inplace=True)
            
            generated_count += 4
            logger.info(f"Extracted datetime features for {col}")
            
        except Exception as e:
            logger.error(f"Failed to extract datetime features for {col}: {e}")
            # If it fails completely, we drop it to keep the matrix clean
            df.drop(columns=[col], inplace=True, errors='ignore')
            
    return df, generated_count
