import pandas as pd
import io
import logging
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from database import db

logger = logging.getLogger(__name__)

async def validate_dataset(dataset_id: str):
    logger.info(f"Starting validation for dataset: {dataset_id}")
    
    # 1. Fetch metadata from datasets collection
    try:
        dataset_oid = ObjectId(dataset_id)
    except Exception:
        logger.error(f"Invalid dataset_id format (not an ObjectId): {dataset_id}")
        return

    dataset = await db.datasets.find_one({"_id": dataset_oid})
    if not dataset:
        logger.error(f"Dataset {dataset_id} not found in database.")
        return
        
    file_id = dataset.get("fileId")
    if not file_id:
        logger.error(f"Dataset {dataset_id} has no fileId.")
        return

    # 2. Download from GridFS
    fs = AsyncIOMotorGridFSBucket(db)
    try:
        grid_out = await fs.open_download_stream(ObjectId(file_id))
        file_data = await grid_out.read()
    except Exception as e:
        logger.error(f"Failed to read file from GridFS: {e}")
        await db.datasets.update_one({"_id": dataset_oid}, {"$set": {"status": "failed", "validationError": str(e)}})
        return

    # 3. Load into Pandas
    try:
        df = pd.read_csv(io.BytesIO(file_data))
    except Exception as e:
        logger.error(f"Pandas failed to parse CSV: {e}")
        await db.datasets.update_one({"_id": dataset_oid}, {"$set": {"status": "failed", "validationError": "Invalid CSV format"}})
        return

    # 4. Run Validation Heuristics
    report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "issues_found": []
    }

    # Missing values check
    missing_counts = df.isnull().sum()
    for col, count in missing_counts.items():
        if count > 0:
            percentage = (count / len(df)) * 100
            severity = "HIGH" if percentage > 50 else "MEDIUM"
            report["issues_found"].append({
                "type": "MISSING_VALUES",
                "column": col,
                "count": int(count),
                "percentage": round(percentage, 2),
                "severity": severity
            })

    # Duplicate rows check
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        report["issues_found"].append({
            "type": "DUPLICATE_ROWS",
            "count": int(duplicates),
            "severity": "LOW"
        })

    # Constant columns check
    for col in df.columns:
        if df[col].nunique() <= 1:
            report["issues_found"].append({
                "type": "CONSTANT_COLUMN",
                "column": col,
                "severity": "MEDIUM"
            })

    # 5. Update MongoDB
    await db.datasets.update_one(
        {"_id": dataset_oid},
        {"$set": {
            "status": "validated",
            "currentStep": 4,
            "validationReport": report
        }}
    )
    logger.info(f"Successfully validated dataset {dataset_id}")
