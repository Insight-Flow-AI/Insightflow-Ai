import pandas as pd
from sklearn.preprocessing import LabelEncoder
import logging

logger = logging.getLogger(__name__)

def encode_categorical_features(df: pd.DataFrame, cat_cols: list, target_col: str = None) -> tuple[pd.DataFrame, dict, int]:
    """
    Applies Label Encoding for binary features/target and OHE for low-cardinality nominals.
    Fallback to Label Encoding for high cardinality (>10).
    Returns DataFrame, encoder state dictionary, and number of generated features.
    """
    encoders = {}
    generated_count = 0
    
    # 1. Always Label Encode the Target Column if it's categorical
    if target_col and target_col in df.columns and df[target_col].dtype == 'object':
        le = LabelEncoder()
        df[target_col] = le.fit_transform(df[target_col].astype(str))
        encoders[target_col] = {'type': 'LabelEncoder', 'classes': le.classes_.tolist()}
        logger.info(f"Label encoded target column: {target_col}")

    # 2. Process remaining categorical columns
    for col in cat_cols:
        if col not in df.columns or col == target_col:
            continue
            
        unique_vals = df[col].nunique()
        
        # Binary or High Cardinality -> LabelEncoder
        if unique_vals == 2 or unique_vals >= 10:
            le = LabelEncoder()
            # Handle potential NaNs silently by coercing to string
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = {'type': 'LabelEncoder', 'classes': le.classes_.tolist()}
            logger.info(f"Label encoded {col} (Unique values: {unique_vals})")
            
        # Low Cardinality Nominal -> One-Hot Encoding
        elif 2 < unique_vals < 10:
            # We use pd.get_dummies for MVP
            dummies = pd.get_dummies(df[col], prefix=col, dummy_na=False).astype(int)
            df = pd.concat([df, dummies], axis=1)
            df.drop(columns=[col], inplace=True)
            
            encoders[col] = {'type': 'OneHotEncoder', 'new_columns': dummies.columns.tolist()}
            generated_count += len(dummies.columns) - 1 # Net new columns
            logger.info(f"One-Hot encoded {col} into {len(dummies.columns)} columns")
            
    return df, encoders, generated_count
