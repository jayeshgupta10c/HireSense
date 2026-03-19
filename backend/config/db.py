"""
config/db.py — MongoDB connection manager
"""
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME   = os.getenv("DB_NAME", "hiresense")

_client: MongoClient | None = None


def get_db():
    """Return the hiresense database, creating a client if needed."""
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        try:
            _client.admin.command("ping")
            print(f"[DB] Connected to MongoDB at {MONGO_URI}")
        except ConnectionFailure as exc:
            print(f"[DB] MongoDB unreachable: {exc}")
            raise
    return _client[DB_NAME]