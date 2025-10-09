"""
MongoDB Configuration and Connection Manager
"""
import os
from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MongoDBManager:
    """Singleton MongoDB connection manager"""

    _instance: Optional['MongoDBManager'] = None
    _client: Optional[MongoClient] = None
    _db: Optional[Database] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize MongoDB connection"""
        if self._client is None:
            # Get MongoDB connection string from environment
            mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            db_name = os.getenv('MONGODB_DATABASE', 'aitutor')

            try:
                self._client = MongoClient(mongo_uri)
                self._db = self._client[db_name]

                # Test connection
                self._client.admin.command('ping')
                print(f"✅ Connected to MongoDB: {db_name}")

            except Exception as e:
                print(f"❌ Failed to connect to MongoDB: {e}")
                print("⚠️  Falling back to local file storage")
                self._client = None
                self._db = None

    @property
    def db(self) -> Optional[Database]:
        """Get database instance"""
        return self._db

    @property
    def client(self) -> Optional[MongoClient]:
        """Get MongoDB client instance"""
        return self._client

    def is_connected(self) -> bool:
        """Check if MongoDB is connected"""
        return self._db is not None

    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            print("MongoDB connection closed")

# Global instance
mongodb = MongoDBManager()
