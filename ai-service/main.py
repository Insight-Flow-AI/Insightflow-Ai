import os
import json
import asyncio
import logging
from fastapi import FastAPI
from confluent_kafka import Consumer, KafkaError
from preprocessing.cleaner import clean_dataset
from preprocessing.validator import validate_dataset

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="InsightFlow AI Service")

KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = "dataset-upload"

async def process_dataset_pipeline(dataset_id: str):
    logger.info(f"Starting pipeline for dataset: {dataset_id}")
    await validate_dataset(dataset_id)
    await clean_dataset(dataset_id)
    logger.info(f"Finished pipeline for dataset: {dataset_id}")

async def consume_kafka():
    conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'group.id': 'ai-service-group',
        'auto.offset.reset': 'earliest'
    }
    
    # We delay start to ensure Kafka broker is fully up during docker compose
    await asyncio.sleep(5)
    
    try:
        consumer = Consumer(conf)
        consumer.subscribe([KAFKA_TOPIC, "feature-engineering", "feature-engineered", "dataset-understood", "problem-detected", "model-selection-complete"])
        logger.info(f"Subscribed to Kafka topics: {KAFKA_TOPIC}, feature-engineering, feature-engineered, dataset-understood, problem-detected, model-selection-complete at {KAFKA_BROKER}")
    except Exception as e:
        logger.error(f"Failed to connect to Kafka: {e}")
        return

    while True:
        # Use asyncio.to_thread to prevent the blocking poll from freezing FastAPI
        msg = await asyncio.to_thread(consumer.poll, 1.0)
        
        if msg is None:
            await asyncio.sleep(0.1) # Prevent busy loop if poll returns immediately
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                await asyncio.sleep(0.1)
                continue
            logger.error(f"Kafka error: {msg.error()}")
            await asyncio.sleep(1.0) # Sleep longer on actual errors
            continue

        try:
            payload = json.loads(msg.value().decode('utf-8'))
            topic = msg.topic()
            logger.info(f"Received Kafka event on {topic}: {payload}")
            
            # Note: Phase 4 passes dataset_id as "dataset_id" instead of "datasetId"
            dataset_id = payload.get("datasetId") or payload.get("dataset_id")
            if dataset_id:
                if topic == KAFKA_TOPIC:
                    # Trigger the Phase 2 & 3 pipeline asynchronously
                    asyncio.create_task(process_dataset_pipeline(dataset_id))
                elif topic == "feature-engineering":
                    # Trigger the Phase 4 pipeline asynchronously
                    from feature_engineering.engineer import process_feature_engineering
                    asyncio.create_task(process_feature_engineering(dataset_id))
                elif topic == "feature-engineered":
                    # Trigger the Phase 5 pipeline asynchronously
                    from dataset_understanding.orchestrator import process_dataset_understanding
                    asyncio.create_task(process_dataset_understanding(dataset_id))
                elif topic == "dataset-understood":
                    # Trigger the Phase 6 pipeline asynchronously
                    from problem_detection.orchestrator import process_problem_detection
                    asyncio.create_task(process_problem_detection(dataset_id))
                elif topic == "problem-detected":
                    # Trigger the Phase 7 pipeline asynchronously
                    from model_selection.selector import process_model_selection
                    asyncio.create_task(process_model_selection(dataset_id))
                elif topic == "model-selection-complete":
                    # Trigger the Phase 8 pipeline asynchronously
                    from model_training.orchestrator import process_model_training
                    asyncio.create_task(process_model_training(dataset_id))
        except Exception as e:
            logger.error(f"Failed to process Kafka message: {e}")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Service...")
    asyncio.create_task(consume_kafka())

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-service"}
