import os
import json
import asyncio
import logging
from fastapi import FastAPI
from confluent_kafka import Consumer, KafkaError
from preprocessing.validator import validate_dataset

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="InsightFlow AI Service")

KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = "dataset-upload"

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
        consumer.subscribe([KAFKA_TOPIC])
        logger.info(f"Subscribed to Kafka topic: {KAFKA_TOPIC} at {KAFKA_BROKER}")
    except Exception as e:
        logger.error(f"Failed to connect to Kafka: {e}")
        return

    while True:
        # Use asyncio.to_thread to prevent the blocking poll from freezing FastAPI
        msg = await asyncio.to_thread(consumer.poll, 1.0)
        
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            logger.error(f"Kafka error: {msg.error()}")
            continue

        try:
            payload = json.loads(msg.value().decode('utf-8'))
            logger.info(f"Received Kafka event: {payload}")
            
            dataset_id = payload.get("datasetId")
            if dataset_id:
                # Trigger validation asynchronously
                asyncio.create_task(validate_dataset(dataset_id))
        except Exception as e:
            logger.error(f"Failed to process Kafka message: {e}")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting AI Service...")
    asyncio.create_task(consume_kafka())

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ai-service"}
