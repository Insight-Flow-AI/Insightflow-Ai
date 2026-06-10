import json
import logging
import os
from confluent_kafka import Producer

logger = logging.getLogger(__name__)
KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

def get_producer():
    conf = {'bootstrap.servers': KAFKA_BROKER}
    return Producer(conf)

def publish_model_selection_complete(dataset_id: str):
    producer = get_producer()
    topic = "model-selection-complete"
    payload = json.dumps({
        "datasetId": dataset_id,
        "status": "MODEL_SELECTION_COMPLETE"
    })
    
    try:
        producer.produce(topic, payload.encode('utf-8'))
        producer.flush()
        logger.info(f"Published event to {topic} for dataset {dataset_id}")
    except Exception as e:
        logger.error(f"Failed to publish to {topic}: {e}")
