import pandas as pd
import io
import json
import os
import logging
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from confluent_kafka import Producer
from database import db

from .datetime_features import extract_datetime_features
from .encoder import encode_categorical_features
from .scaler import scale_numerical_features
from .feature_selector import select_features
from .report_generator import generate_feature_report

logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_NEXT = "feature-engineered"

# Kafka Producer Configuration
producer_conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'client.id': 'ai-service-engineer'
}
producer = Producer(producer_conf)

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"[Phase 4] Message delivery failed: {err}")
    else:
        logger.info(f"[Phase 4] Triggered Phase 5 on {msg.topic()} [{msg.partition()}]")

async def process_feature_engineering(dataset_id: str):
    """
    Orchestrates Phase 4: Feature Engineering
    """
    logger.info(f"Starting Phase 4 (Feature Engineering) for dataset {dataset_id}")
    
    # 1. Fetch dataset metadata
    dataset = await db.datasets.find_one({"_id": ObjectId(dataset_id)})
    if not dataset:
        logger.error(f"Dataset {dataset_id} not found.")
        return
        
    cleaned_file_id = dataset.get("cleanedFileId")
    if not cleaned_file_id:
        logger.error(f"No cleanedFileId found for {dataset_id}. Cannot engineer features.")
        return
        
    # 2. Download cleaned CSV from GridFS
    try:
        fs = AsyncIOMotorGridFSBucket(db)
        grid_out = await fs.open_download_stream(ObjectId(cleaned_file_id))
        file_data = await grid_out.read()
        df = pd.read_csv(io.BytesIO(file_data), on_bad_lines='skip', engine='python')
    except Exception as e:
        logger.error(f"Failed to read cleaned CSV from GridFS: {e}")
        return

    original_cols_count = len(df.columns)
    
    # 3. Detect Column Types & Target
    # We infer types directly from pandas to be safe, but prioritize target from validationReport
    target_col = None
    if "validationReport" in dataset and "target_column" in dataset["validationReport"]:
        target_col = dataset["validationReport"]["target_column"]
        
    datetime_cols = df.select_dtypes(include=['datetime64', 'datetimetz']).columns.tolist()
    # Also check string columns that might be dates
    for col in df.select_dtypes(include=['object']).columns:
        if 'date' in col.lower() or 'time' in col.lower():
            datetime_cols.append(col)
            
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    # Remove datetime cols from cat_cols if they were caught
    cat_cols = [c for c in cat_cols if c not in datetime_cols]
    
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    # 4. Extract Datetime Features
    df, dt_generated = extract_datetime_features(df, datetime_cols)
    
    # 5. Encode Categorical Features
    # Recalculate cat_cols in case they changed
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    df, encoder_metadata, enc_generated = encode_categorical_features(df, cat_cols, target_col)
    
    # 6. Scale Numerical Features
    # Recalculate num_cols as OHE generated new numeric columns
    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    df, scaler_metadata = scale_numerical_features(df, num_cols, target_col)
    
    # 7. Feature Selection (Drop highly correlated)
    df, dropped_cols = select_features(df, target_col)
    
    final_cols_count = len(df.columns)
    
    # 8. Generate Report
    report = generate_feature_report(
        original_columns=original_cols_count,
        encoded_columns=enc_generated,
        scaled_columns=len(scaler_metadata.get('features', [])),
        removed_columns=len(dropped_cols),
        final_columns=final_cols_count,
        encoder_metadata=encoder_metadata,
        scaler_metadata=scaler_metadata
    )
    
    # 9. Save Engineered Dataset to GridFS
    try:
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        fs = AsyncIOMotorGridFSBucket(db)
        engineered_file_id = await fs.upload_from_stream(
            f"feature_engineered_{dataset_id}.csv",
            csv_buffer,
            metadata={"datasetId": dataset_id, "type": "engineered"}
        )
        
        # Update MongoDB
        await db.datasets.update_one(
            {"_id": ObjectId(dataset_id)},
            {"$set": {
                "status": "feature_engineered",
                "currentStep": 5,
                "engineeredFileId": str(engineered_file_id),
                "featureReport": report
            }}
        )
        # Trigger Phase 5 via Kafka
        try:
            event_payload = {
                "dataset_id": str(dataset_id),
                "status": "FEATURE_ENGINEERED"
            }
            producer.produce(
                KAFKA_TOPIC_NEXT, 
                json.dumps(event_payload).encode('utf-8'), 
                callback=delivery_report
            )
            producer.poll(0)
        except Exception as e:
            logger.error(f"[Phase 4] Failed to publish Kafka event for Phase 5: {e}")
            
        return True
    except Exception as e:
        logger.error(f"Failed to save engineered dataset: {e}")
        return False
