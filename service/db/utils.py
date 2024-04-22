from motor.motor_asyncio import AsyncIOMotorClient

# Local
from constants import MONGO_URL
from .client import db


async def connect_to_mongodb():
    db.client = AsyncIOMotorClient(MONGO_URL)


async def close_mongodb_connection():
    db.client.close()
