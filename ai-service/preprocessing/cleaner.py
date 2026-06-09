import io
import os
import json
import logging
import pandas as pd
import numpy as np
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from confluent_kafka import Producer

from database import db

logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_NEXT = "feature-engineering"

# Kafka Producer Configuration
producer_conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'client.id': 'ai-service-cleaner'
}
producer = Producer(producer_conf)

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"[Phase 3] Message delivery failed: {err}")
    else:
        logger.info(f"[Phase 3] Triggered Phase 4 on {msg.topic()} [{msg.partition()}]")

class DataCleaningService:
    def __init__(self, validation_report: dict, target_column: str = None):
        self.report = validation_report
        self.target_column = target_column

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        cleaned_df = df.copy()
        findings = self.report.get("findings", [])

        # 0. Handle Duplicate Column Names
        duplicate_flag = any(f.get("action") == "RENAME_DUPLICATE_COLUMNS" for f in findings)
        if duplicate_flag or cleaned_df.columns.duplicated().any():
            cols = pd.Series(cleaned_df.columns)
            for dup in cols[cols.duplicated()].unique():
                cols[cols[cols == dup].index.values.tolist()] = [
                    f"{dup}_{i+1}" for i in range(sum(cols == dup))
                ]
            cleaned_df.columns = cols
            logger.info("Renamed duplicate columns.")

        # 1. Drop columns based on validation findings
        cols_to_drop = set()
        for finding in findings:
            if finding.get("action") in ["DROP_COLUMN", "DROP_ZERO_VARIANCE_COLUMN"]:
                col = finding.get("column")
                if col and col in cleaned_df.columns:
                    cols_to_drop.add(col)
                    
        if cols_to_drop:
            cleaned_df.drop(columns=list(cols_to_drop), inplace=True)
            logger.info(f"Dropped columns: {cols_to_drop}")

        # 2. Target Variable Handling: Drop rows with missing targets
        if self.target_column and self.target_column in cleaned_df.columns:
            missing_target_count = cleaned_df[self.target_column].isnull().sum()
            if missing_target_count > 0:
                cleaned_df.dropna(subset=[self.target_column], inplace=True)
                logger.info(f"Dropped {missing_target_count} rows due to missing target variable.")

        # 3. Impute missing values
        schema_map = self.report.get("schema_map", {})
        for col in cleaned_df.columns:
            if col == self.target_column:
                continue # Do not impute the target variable

            if cleaned_df[col].isnull().any():
                col_type = schema_map.get(col, {}).get("detected_type", "UNKNOWN")
                if col_type == "NUMERIC":
                    median = cleaned_df[col].median()
                    # Fallback to 0 if median is NaN
                    val = 0 if pd.isna(median) else median
                    cleaned_df[col].fillna(val, inplace=True)
                else:
                    mode_series = cleaned_df[col].mode()
                    mode_val = mode_series.iloc[0] if not mode_series.empty else "Unknown"
                    cleaned_df[col].fillna(mode_val, inplace=True)

        # 4. Outlier Mitigation (IQR Capping)
        stats = self.report.get("stats_summary", {})
        for col in cleaned_df.columns:
            col_stats = stats.get(col)
            if col_stats and col_stats.get("outlier_pct", 0) > 0:
                lower = col_stats["iqr_bounds"]["lower"]
                upper = col_stats["iqr_bounds"]["upper"]
                # Capping
                cleaned_df[col] = np.where(cleaned_df[col] < lower, lower, cleaned_df[col])
                cleaned_df[col] = np.where(cleaned_df[col] > upper, upper, cleaned_df[col])

        # 5. Skewness Transformations
        for finding in findings:
            col = finding.get("column")
            if not col or col not in cleaned_df.columns:
                continue
            
            action = finding.get("action")
            if action == "APPLY_LOG_TRANSFORM":
                # Ensure values are strictly positive before log1p
                min_val = cleaned_df[col].min()
                if min_val < 0:
                    cleaned_df[col] = cleaned_df[col] - min_val
                cleaned_df[col] = np.log1p(cleaned_df[col])
                logger.info(f"Applied log transform to {col}")
            
            elif action == "CONSIDER_SQRT_TRANSFORM":
                min_val = cleaned_df[col].min()
                if min_val < 0:
                    cleaned_df[col] = cleaned_df[col] - min_val
                cleaned_df[col] = np.sqrt(cleaned_df[col])
                logger.info(f"Applied sqrt transform to {col}")

        # 6. Deduplication (Flag instead of blind drop if needed, but for now drop safe)
        initial_rows = len(cleaned_df)
        cleaned_df.drop_duplicates(inplace=True)
        final_rows = len(cleaned_df)
        if initial_rows != final_rows:
            logger.info(f"Dropped {initial_rows - final_rows} duplicate rows.")

        return cleaned_df

async def clean_dataset(dataset_id: str):
    logger.info(f"[Phase 3] Cleaning started for dataset: {dataset_id}")

    try:
        dataset_oid = ObjectId(dataset_id)
    except Exception:
        logger.error(f"[Phase 3] Invalid dataset_id: {dataset_id}")
        return

    dataset = await db.datasets.find_one({"_id": dataset_oid})
    if not dataset:
        logger.error(f"[Phase 3] Dataset not found: {dataset_id}")
        return

    if dataset.get("status") in ["failed", "validation_failed"]:
        logger.info(f"[Phase 3] Skipping dataset {dataset_id} due to failed status.")
        return

    file_id = dataset.get("fileId")
    validation_report = dataset.get("validationReport")
    target_column = dataset.get("targetColumn")

    if not file_id or not validation_report:
        logger.error(f"[Phase 3] Missing fileId or validationReport for dataset: {dataset_id}")
        return

    fs = AsyncIOMotorGridFSBucket(db)
    try:
        grid_out = await fs.open_download_stream(ObjectId(file_id))
        file_data = await grid_out.read()
    except Exception as e:
        logger.error(f"[Phase 3] GridFS read failed: {e}")
        return

    try:
        df = pd.read_csv(io.BytesIO(file_data))
    except Exception as e:
        logger.error(f"[Phase 3] CSV parse failed: {e}")
        return

    # Run cleaning
    try:
        service = DataCleaningService(validation_report, target_column)
        cleaned_df = service.clean(df)
    except Exception as e:
        logger.error(f"[Phase 3] Cleaning failed: {e}")
        await db.datasets.update_one(
            {"_id": dataset_oid},
            {"$set": {"status": "cleaning_failed", "cleaningError": str(e)}}
        )
        return

    # Upload cleaned CSV to GridFS
    try:
        csv_buffer = io.BytesIO()
        cleaned_df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        cleaned_file_id = await fs.upload_from_stream(
            f"cleaned_{dataset_id}.csv",
            csv_buffer,
            metadata={"datasetId": dataset_id, "type": "cleaned"}
        )
    except Exception as e:
        logger.error(f"[Phase 3] GridFS write failed: {e}")
        return

    # Update MongoDB
    await db.datasets.update_one(
        {"_id": dataset_oid},
        {"$set": {
            "status": "cleaned",
            "currentStep": 4,
            "cleanedFileId": str(cleaned_file_id),
            "cleanedRows": len(cleaned_df),
            "cleanedCols": len(cleaned_df.columns)
        }}
    )

    logger.info(f"[Phase 3] Done — dataset={dataset_id} | Cleaned rows={len(cleaned_df)}")

    # Trigger Phase 4 via Kafka
    try:
        event_payload = {"datasetId": str(dataset_id)}
        producer.produce(
            KAFKA_TOPIC_NEXT, 
            json.dumps(event_payload).encode('utf-8'), 
            callback=delivery_report
        )
        producer.poll(0)
    except Exception as e:
        logger.error(f"[Phase 3] Failed to publish Kafka event for Phase 4: {e}")
