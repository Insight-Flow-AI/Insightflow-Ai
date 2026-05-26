import os
import logging

from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/insightflow")

# Always explicitly use 'insightflow' — get_default_database() can fail
# with Atlas URIs that have query params after the database name
client = AsyncIOMotorClient(MONGO_URI)
db = client["insightflow"]

logger.info(f"[DB] MongoDB client initialised — URI prefix: {MONGO_URI[:40]}...")
