from motor.motor_asyncio import AsyncIOMotorClient

from app.core.settings import MONGO_URI, MONGO_DB
# MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB]
