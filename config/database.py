from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import certifi
import os
import logging

load_dotenv()

class DatabaseConfig:
    def __init__(self):
        self.client = None
        self.db = None
        
    def get_uri(self):
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            raise ValueError("MongoDB URI not found in environment variables")
        if not any(x in mongodb_uri for x in ['mongodb://', 'mongodb+srv://']):
            raise ValueError("Invalid MongoDB URI format")
        return mongodb_uri

    def get_database_name(self):
        db_name = os.getenv('MONGODB_DATABASE', 'DRD_GAN')
        if not db_name:
            raise ValueError("Database name not found in environment variables")
        return db_name

    async def connect(self):
        try:
            mongodb_uri = self.get_uri()
            
            # Create new client with connection pooling and SSL certificate verification
            self.client = AsyncIOMotorClient(
                mongodb_uri,
                server_api=ServerApi('1'),
                maxPoolSize=50,
                minPoolSize=10,
                tlsCAFile=certifi.where(),
                connectTimeoutMS=5000,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection before proceeding
            try:
                await self.client.admin.command('ping')
                print("Successfully connected to MongoDB!")
            except Exception as e:
                print(f"Failed to connect to MongoDB: {str(e)}")
                if "bad auth" in str(e):
                    print("Authentication failed. Please check your MongoDB credentials.")
                raise

            self.db = self.client[self.get_database_name()]
            return self.db
            
        except Exception as e:
            print(f"Error connecting to MongoDB: {str(e)}")
            # Close client if it was created
            if self.client:
                self.client.close()
            raise
    
    async def close(self):
        if self.client:
            self.client.close() 