from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None

    async def connect_to_database(self):
        try:
            logger.info("Attempting to connect to MongoDB...")
            # Use direct connection to local MongoDB
            self.client = AsyncIOMotorClient(
                "mongodb://localhost:27017",
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            self.db = self.client[settings.DB_NAME]
            
            # Verify connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB!")
            
            # Create indexes if they don't exist
            await self.db.users.create_index("email", unique=True)
            logger.info("Database indexes created/verified")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise Exception(f"Could not connect to MongoDB: {str(e)}")

    async def close_database_connection(self):
        if self.client is not None:
            self.client.close()
            logger.info("MongoDB connection closed")

    def get_db(self):
        if self.db is None:
            raise Exception("Database not initialized")
        return self.db

db = Database()
