
from motor.motor_asyncio import AsyncIOMotorClient
import os

DB_CONNECT_URL = os.getenv("DB_CONNECTION","mongodb://davidn:cisco@127.0.0.1:27017/")
client = AsyncIOMotorClient(DB_CONNECT_URL)
db = client.webservices

async def get_database():
    yield db

