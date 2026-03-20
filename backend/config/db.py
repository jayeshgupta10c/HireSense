"""
config/db.py — MongoDB Atlas connection
"""
import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Paste your full Atlas URI here as the default fallback for local testing
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://Ram:RamaRam@cluster0.jqpsivv.mongodb.net/hiresense?retryWrites=true&w=majority&appName=Cluster0"
)

DB_NAME = os.getenv("DB_NAME", "hiresense")

_client = None


def get_db():
    global _client
    if _client is None:
        print(f"[DB] Connecting to MongoDB...")
        print(f"[DB] URI starts with: {MONGO_URI[:40]}...")
        
        _client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            tls=True,
            tlsAllowInvalidCertificates=False
        )
        
        try:
            # Force connection test
            _client.admin.command("ping")
            print(f"[DB] ✓ Connected to MongoDB Atlas successfully!")
            print(f"[DB] Using database: {DB_NAME}")
        except ServerSelectionTimeoutError as exc:
            print(f"[DB] ✗ Connection TIMEOUT: {exc}")
            print(f"[DB] Check: 1) IP whitelist on Atlas  2) Password correct  3) Internet connection")
            _client = None
            raise
        except ConnectionFailure as exc:
            print(f"[DB] ✗ Connection FAILED: {exc}")
            _client = None
            raise
        except Exception as exc:
            print(f"[DB] ✗ Unexpected error: {exc}")
            _client = None
            raise
            
    return _client[DB_NAME]


def test_connection():
    """Call this to manually test your Atlas connection."""
    try:
        db = get_db()
        collections = db.list_collection_names()
        print(f"[DB] Collections in '{DB_NAME}': {collections}")
        
        # Try inserting and reading a test document
        test_col = db["connection_test"]
        result = test_col.insert_one({"test": "hello", "status": "working"})
        print(f"[DB] ✓ Test insert successful. ID: {result.inserted_id}")
        
        found = test_col.find_one({"_id": result.inserted_id})
        print(f"[DB] ✓ Test read successful: {found}")
        
        test_col.delete_one({"_id": result.inserted_id})
        print(f"[DB] ✓ Test delete successful. Connection fully working!")
        return True
    except Exception as e:
        print(f"[DB] ✗ Test failed: {e}")
        return False


if __name__ == "__main__":
    # Run this file directly to test: python config/db.py
    print("Testing MongoDB Atlas connection...")
    test_connection()