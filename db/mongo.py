import os
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # Imported only for type checking; no runtime dependency
    from pymongo import MongoClient

_client: Optional["MongoClient"] = None


def get_collection():
    global _client
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    mongo_db = os.environ.get("MONGO_DB", "appdb")
    mongo_collection = os.environ.get("MONGO_COLLECTION", "recipes")

    if _client is None:
        try:
            from pymongo import (
                MongoClient,
            )  # local import to avoid hard dep at import time
        except Exception as e:
            raise RuntimeError(
                "pymongo is required. Please install it: pip install pymongo"
            ) from e
        _client = MongoClient(mongo_uri)

    db = _client[mongo_db]
    return db[mongo_collection]
