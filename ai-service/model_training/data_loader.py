import logging
import io
import pandas as pd
from bson.objectid import ObjectId
from sklearn.model_selection import train_test_split
from database import db
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

logger = logging.getLogger(__name__)

async def load_and_split_dataset(dataset_id: str, file_id: str, target_col: str, problem_type: str):
    """
    Loads the engineered dataset from GridFS, separates X and y, and creates
    the Holdout Test Set (20%) for Phase 9.
    Returns: X_train, X_test, y_train, y_test, holdout_file_id
    """
    logger.info(f"Loading engineered dataset {file_id} from GridFS...")
    fs = AsyncIOMotorGridFSBucket(db)
    
    # Load from GridFS
    try:
        grid_out = await fs.open_download_stream(ObjectId(file_id))
        csv_data = await grid_out.read()
        df = pd.read_csv(io.BytesIO(csv_data))
    except Exception as e:
        logger.error(f"Failed to load engineered dataset: {e}")
        raise ValueError(f"Could not load dataset {file_id} from GridFS.")
        
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in dataset")
        
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    if problem_type == "CLASSIFICATION":
        y = y.astype(int)
    
    # Split strategy
    stratify_col = y if problem_type == "CLASSIFICATION" else None
    
    # Handle extremely tiny datasets gracefully (e.g. 10 rows)
    test_size = 0.2
    if len(df) < 50:
        logger.warning(f"Very small dataset detected ({len(df)} rows). Reducing test set to 10% or at least 1 sample.")
        # If stratified, ensure at least 2 samples per class, else train_test_split might fail. We'll use random for tiny datasets if stratify fails
        try:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, stratify=stratify_col, random_state=42)
        except ValueError:
            logger.warning("Stratified split failed due to tiny class size. Falling back to random split.")
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)
    else:
        try:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, stratify=stratify_col, random_state=42)
        except ValueError:
            logger.warning("Stratified split failed (likely class with 1 sample). Falling back to random split.")
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
            
    logger.info(f"Split complete. Train: {len(X_train)} rows, Holdout: {len(X_test)} rows.")
    
    # Save holdout set to GridFS for Phase 9
    holdout_df = pd.concat([X_test, y_test], axis=1)
    holdout_csv = holdout_df.to_csv(index=False).encode('utf-8')
    
    holdout_file_id = await fs.upload_from_stream(
        f"{dataset_id}_holdout_test.csv",
        holdout_csv,
        metadata={"dataset_id": dataset_id, "type": "holdout_test"}
    )
    logger.info(f"Saved Phase 9 Holdout Test Set to GridFS: {holdout_file_id}")
    
    return X_train, X_test, y_train, y_test, str(holdout_file_id)
