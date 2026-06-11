import io
import json
import os
import logging
import pandas as pd
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from confluent_kafka import Producer

from database import db
from .profiler import generate_profile
from .statistics import calculate_descriptive_statistics
from .distribution import analyze_distributions
from .correlation import calculate_correlations
from .target_analysis import analyze_target
from .health_score import calculate_health_score
from .insight_generator import generate_insights
from .viz_metadata import generate_visualization_metadata

logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_NEXT = "dataset-understood"

producer_conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'client.id': 'ai-service-understanding'
}
producer = Producer(producer_conf)

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"[Phase 5] Message delivery failed: {err}")
    else:
        logger.info(f"[Phase 5] Triggered Phase 6 on {msg.topic()} [{msg.partition()}]")

async def process_dataset_understanding(dataset_id: str):
    """
    Orchestrates Phase 5: Dataset Understanding.
    Downloads the engineered dataset, runs statistical analysis, and saves the report.
    """
    logger.info(f"[Phase 5] Starting Dataset Understanding for dataset: {dataset_id}")
    
    try:
        dataset_oid = ObjectId(dataset_id)
        dataset = await db.datasets.find_one({"_id": dataset_oid})
        
        if not dataset:
            logger.error(f"Dataset {dataset_id} not found.")
            return False
            
        engineered_file_id = dataset.get("engineeredFileId")
        if not engineered_file_id:
            logger.error(f"No engineeredFileId found for {dataset_id}. Cannot run understanding.")
            return False
            
        target_col = dataset.get("targetColumn")
        
        # 1. Download Engineered Dataset
        try:
            fs = AsyncIOMotorGridFSBucket(db)
            grid_out = await fs.open_download_stream(ObjectId(engineered_file_id))
            file_data = await grid_out.read()
            df = pd.read_csv(io.BytesIO(file_data), engine='python')
        except Exception as e:
            logger.error(f"Failed to read engineered CSV from GridFS: {e}")
            return False
            
        # 2. Run Analysis Modules
        profile = generate_profile(df, target_col)
        stats = calculate_descriptive_statistics(df)
        distributions = analyze_distributions(df)
        correlations = calculate_correlations(df)
        target_analysis = analyze_target(df, target_col)
        
        health_score = calculate_health_score(distributions, correlations, target_analysis)
        insights = generate_insights(correlations, distributions, target_analysis)
        viz_metadata = generate_visualization_metadata(df)
        
        # 3. Compile Master Report
        understanding_report = {
            "profile": profile,
            "statistics": stats,
            "distributions": distributions,
            "correlations": correlations,
            "targetAnalysis": target_analysis,
            "healthScore": health_score,
            "insights": insights,
            "visualizations": viz_metadata
        }
        
        # 4. Save to MongoDB
        await db.datasets.update_one(
            {"_id": dataset_oid},
            {"$set": {
                "status": "dataset_understood",
                "currentStep": 6,
                "understandingReport": understanding_report
            }}
        )
        logger.info(f"[Phase 5] Successfully saved understanding report for {dataset_id}. Health Score: {health_score}")
        
        # 5. Trigger Phase 6 via Kafka
        try:
            event_payload = {
                "dataset_id": str(dataset_id),
                "status": "DATASET_UNDERSTOOD",
                "health_score": health_score
            }
            producer.produce(
                KAFKA_TOPIC_NEXT, 
                json.dumps(event_payload).encode('utf-8'), 
                callback=delivery_report
            )
            producer.poll(0)
        except Exception as e:
            logger.error(f"[Phase 5] Failed to publish Kafka event for Phase 6: {e}")
            
        return True
        
    except Exception as e:
        logger.error(f"[Phase 5] Unexpected error during dataset understanding: {e}")
        return False
