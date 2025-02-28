from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb://localhost:27018"
DB_NAME = "admin_db"

client = AsyncIOMotorClient(MONGO_URI)
database = client[DB_NAME]

def get_database():
    return database


