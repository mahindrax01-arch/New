from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import get_settings

settings = get_settings()
client = AsyncIOMotorClient(settings.mongodb_uri)
db: AsyncIOMotorDatabase = client[settings.mongodb_db]


def get_collection(name: str):
    return db[name]
