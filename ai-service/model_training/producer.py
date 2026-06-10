import os
import json
import logging
from confluent_kafka import Producer

logger = logging.getLogger(__name__)

KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC = "models-trained"

try:
    producer = Producer({'bootstrap.servers': KAFKA_BROKER})
except Exception as e:
    logger.error(f"Failed to initialize Kafka Producer in Phase 8: {e}")
    producer = None

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed: {err}")
    else:
        logger.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def publish_models_trained(dataset_id: str, holdout_file_id: str):
    """
    Publishes the Phase 8 completion event to Kafka to trigger Phase 9 (Evaluation).
    """
    if producer is None:
        logger.error("Kafka producer is not available.")
        return

    payload = {
        "datasetId": dataset_id,
        "status": "MODELS_TRAINED",
        "holdoutDataId": holdout_file_id
    }

    try:
        producer.produce(
            topic=TOPIC,
            key=dataset_id,
            value=json.dumps(payload).encode('utf-8'),
            callback=delivery_report
        )
        producer.flush()
        logger.info(f"Published event to {TOPIC} for dataset {dataset_id}")
    except Exception as e:
        logger.error(f"Failed to publish to Kafka topic {TOPIC}: {e}")
