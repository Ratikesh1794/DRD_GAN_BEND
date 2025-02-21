from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import certifi
import os

load_dotenv()

class DatabaseConfig:
    def __init__(self):
        self.client = None
        self.db = None
        
    def get_uri(self):
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            raise ValueError("MongoDB URI not found in environment variables")
        return mongodb_uri

    def get_database_name(self):
        return os.getenv('MONGODB_DATABASE', 'DRD_GAN')

    async def connect(self):
        try:
            mongodb_uri = self.get_uri()
            
            # Create new client with connection pooling and SSL certificate verification
            self.client = AsyncIOMotorClient(
                mongodb_uri,
                server_api=ServerApi('1'),
                maxPoolSize=50,
                minPoolSize=10,
                tlsCAFile=certifi.where()
            )
            
            db_name = self.get_database_name()
            self.db = self.client[db_name]
            
            # Test connection
            await self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
            
            return self.db
            
        except Exception as e:
            print(f"Error connecting to MongoDB: {str(e)}")
            raise
    
    async def close(self):
        if self.client:
            await self.client.close() 