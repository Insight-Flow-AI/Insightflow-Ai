import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27018/insightflow")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_default_database()
