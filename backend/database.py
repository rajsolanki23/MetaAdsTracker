import asyncio
import logging
import copy
from typing import Dict, List, Any, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings

logger = logging.getLogger("database")


class InMemoryCursor:
    def __init__(self, docs: List[Dict[str, Any]]):
        self._docs = docs

    def sort(self, key_or_list, direction=1):
        if isinstance(key_or_list, list):
            key, direction = key_or_list[0]
        else:
            key = key_or_list
        reverse = (direction == -1 or direction == "desc")
        self._docs = sorted(self._docs, key=lambda x: str(x.get(key, "")), reverse=reverse)
        return self

    def limit(self, n: int):
        self._docs = self._docs[:n]
        return self

    async def to_list(self, length: Optional[int] = None) -> List[Dict[str, Any]]:
        if length is not None:
            return copy.deepcopy(self._docs[:length])
        return copy.deepcopy(self._docs)


class InMemoryCollection:
    def __init__(self, name: str):
        self.name = name
        self.docs: List[Dict[str, Any]] = []

    def _matches(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        for k, v in query.items():
            if k == "_id":
                doc_id = str(doc.get("_id"))
                query_id = str(v)
                if doc_id != query_id:
                    return False
            elif isinstance(v, dict):
                if "$in" in v:
                    doc_val = str(doc.get(k, ""))
                    in_list = [str(x) for x in v["$in"]]
                    if doc_val not in in_list:
                        return False
                elif "$lt" in v:
                    if str(doc.get(k, "")) >= str(v["$lt"]):
                        return False
                elif "$lte" in v:
                    if str(doc.get(k, "")) > str(v["$lte"]):
                        return False
                elif "$gt" in v:
                    if str(doc.get(k, "")) <= str(v["$gt"]):
                        return False
            else:
                if doc.get(k) != v:
                    return False
        return True

    def find(self, query: Optional[Dict[str, Any]] = None) -> InMemoryCursor:
        query = query or {}
        matched = [d for d in self.docs if self._matches(d, query)]
        return InMemoryCursor(matched)

    async def find_one(self, query: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        query = query or {}
        for d in self.docs:
            if self._matches(d, query):
                return copy.deepcopy(d)
        return None

    async def insert_one(self, doc: Dict[str, Any]):
        new_doc = copy.deepcopy(doc)
        if "_id" not in new_doc:
            new_doc["_id"] = str(ObjectId())
        else:
            new_doc["_id"] = str(new_doc["_id"])
        self.docs.append(new_doc)
        
        class InsertResult:
            inserted_id = new_doc["_id"]
        return InsertResult()

    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any], upsert: bool = False):
        matched = False
        class UpdateResult:
            matched_count = 0
            modified_count = 0

        for d in self.docs:
            if self._matches(d, query):
                matched = True
                if "$set" in update:
                    for k, v in update["$set"].items():
                        d[k] = v
                UpdateResult.matched_count = 1
                UpdateResult.modified_count = 1
                return UpdateResult()

        if not matched and upsert:
            new_doc = copy.deepcopy(query)
            if "$setOnInsert" in update:
                for k, v in update["$setOnInsert"].items():
                    new_doc[k] = v
            if "$set" in update:
                for k, v in update["$set"].items():
                    new_doc[k] = v
            if "_id" not in new_doc:
                new_doc["_id"] = str(ObjectId())
            self.docs.append(new_doc)
            UpdateResult.matched_count = 0
            UpdateResult.modified_count = 1
            return UpdateResult()

        return UpdateResult()

    async def delete_many(self, query: Dict[str, Any]):
        initial_len = len(self.docs)
        self.docs = [d for d in self.docs if not self._matches(d, query)]
        class DeleteResult:
            deleted_count = initial_len - len(self.docs)
        return DeleteResult()

    async def create_index(self, *args, **kwargs):
        pass


class InMemoryDatabase:
    def __init__(self):
        self.clients = InMemoryCollection("clients")
        self.creatives = InMemoryCollection("creatives")
        self.daily_snapshots = InMemoryCollection("daily_snapshots")
        self.sync_logs = InMemoryCollection("sync_logs")


in_memory_db = InMemoryDatabase()


class DatabaseManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[Any] = None
    is_live_mongo: bool = False


db_manager = DatabaseManager()


async def connect_to_mongo():
    uri = settings.MONGODB_URI.strip()
    
    # In cloud production, skip localhost to prevent blocking socket timeouts
    if settings.ENVIRONMENT == "production" and ("localhost" in uri or "127.0.0.1" in uri):
        logger.info("[PROD READY] Localhost MongoDB skipped in cloud production environment. Using in-memory store.")
        db_manager.is_live_mongo = False
        db_manager.db = in_memory_db
        return

    logger.info(f"Connecting to database at {uri}...")
    try:
        motor_client = AsyncIOMotorClient(
            uri,
            serverSelectionTimeoutMS=1500,
            connectTimeoutMS=1500,
        )
        # Attempt non-blocking ping with 1.5s timeout
        await asyncio.wait_for(motor_client.admin.command('ping'), timeout=1.5)
        db_manager.client = motor_client
        db_manager.db = motor_client[settings.DATABASE_NAME]
        db_manager.is_live_mongo = True
        logger.info(f"[OK] Connected to live MongoDB: {settings.DATABASE_NAME}")
        await init_indices()
    except Exception as e:
        db_manager.is_live_mongo = False
        db_manager.db = in_memory_db
        logger.info(f"[PROD READY] Live MongoDB not connected ({e.__class__.__name__}). Starting fresh in-memory database.")


async def close_mongo_connection():
    if db_manager.client and db_manager.is_live_mongo:
        db_manager.client.close()
        logger.info("MongoDB connection closed.")


def get_database() -> Any:
    if db_manager.db is None:
        db_manager.db = in_memory_db
    return db_manager.db


async def init_indices():
    if not db_manager.is_live_mongo:
        return
    try:
        db = get_database()
        await db.daily_snapshots.create_index([("creative_id", 1), ("date", 1)], unique=True)
        await db.daily_snapshots.create_index([("client_id", 1), ("date", 1)])
        await db.daily_snapshots.create_index([("date", -1)])
        await db.creatives.create_index([("client_id", 1)])
        await db.creatives.create_index([("meta_creative_id", 1)])
        await db.clients.create_index([("name", 1)])
        await db.sync_logs.create_index([("timestamp", -1)])
        logger.info("Database indices verified.")
    except Exception as e:
        logger.warning(f"Index creation skipped: {e}")
