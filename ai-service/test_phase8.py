import asyncio
import json
import os
from confluent_kafka import Producer

KAFKA_BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

async def trigger_phase_8():
    # Trigger Phase 8 for the user's latest 120-row dataset
    dataset_id = "6a29a9c2ab0f9a235002ce3c"
    
    producer = Producer({'bootstrap.servers': KAFKA_BROKER})
    topic = "model-selection-complete"
    payload = json.dumps({
        "datasetId": dataset_id,
        "status": "READY_FOR_TRAINING",
        "timestamp": 1781112904609
    })
    
    producer.produce(topic, payload.encode('utf-8'))
    producer.flush()
    print(f"Fired Kafka event to {topic} for {dataset_id}. Phase 8 is running!")

if __name__ == "__main__":
    asyncio.run(trigger_phase_8())
