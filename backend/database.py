import logging
import copy
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, date, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
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
    logger.info(f"Connecting to MongoDB at {settings.MONGODB_URI}...")
    try:
        db_manager.client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=1000,
            connectTimeoutMS=1000,
        )
        # Attempt ping
        await db_manager.client.admin.command('ping')
        db_manager.db = db_manager.client[settings.DATABASE_NAME]
        db_manager.is_live_mongo = True
        logger.info(f"[OK] Connected to live MongoDB: {settings.DATABASE_NAME}")
        await init_indices()
    except Exception as e:
        db_manager.is_live_mongo = False
        db_manager.db = in_memory_db
        logger.info(f"[DEMO MODE] Live MongoDB not detected ({e.__class__.__name__}). Using high-speed in-memory store for instant trial demo.")
        seed_in_memory_demo_data()


async def close_mongo_connection():
    if db_manager.client and db_manager.is_live_mongo:
        db_manager.client.close()
        logger.info("MongoDB connection closed.")


def get_database() -> Any:
    if db_manager.db is None:
        db_manager.db = in_memory_db
        seed_in_memory_demo_data()
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


def seed_in_memory_demo_data():
    """
    Populates rich, realistic demo data into the in-memory database if empty.
    """
    if len(in_memory_db.clients.docs) > 0:
        return

    from backend.services.leaderboard_service import evaluate_status, calculate_streak
    import random

    logger.info("Seeding in-memory demo data with realistic client accounts, creatives, and 30-day snapshot histories...")

    clients_data = [
        {
            "_id": "client_aura",
            "name": "Aura Skincare",
            "meta_account_id": "act_849201948",
            "access_token": "EAABdemo_token_aura_skincare_live",
            "target_roas": 2.8,
            "min_spend_threshold": 150.0,
            "currency": "USD",
            "timezone": "America/New_York",
            "is_active": True,
            "created_at": datetime.now(timezone.utc) - timedelta(days=35),
            "updated_at": datetime.now(timezone.utc),
            "last_sync_at": datetime.now(timezone.utc) - timedelta(minutes=25),
            "last_sync_status": "SUCCESS",
            "last_sync_error": None
        },
        {
            "_id": "client_apex",
            "name": "Apex Fitness Apparel",
            "meta_account_id": "act_573829104",
            "access_token": "EAABdemo_token_apex_fitness_live",
            "target_roas": 2.2,
            "min_spend_threshold": 100.0,
            "currency": "USD",
            "timezone": "America/Chicago",
            "is_active": True,
            "created_at": datetime.now(timezone.utc) - timedelta(days=35),
            "updated_at": datetime.now(timezone.utc),
            "last_sync_at": datetime.now(timezone.utc) - timedelta(minutes=45),
            "last_sync_status": "SUCCESS",
            "last_sync_error": None
        },
        {
            "_id": "client_lumina",
            "name": "Lumina Smart Home",
            "meta_account_id": "act_392817402",
            "access_token": "EAABdemo_token_lumina_home_live",
            "target_roas": 3.2,
            "min_spend_threshold": 200.0,
            "currency": "USD",
            "timezone": "America/Los_Angeles",
            "is_active": True,
            "created_at": datetime.now(timezone.utc) - timedelta(days=35),
            "updated_at": datetime.now(timezone.utc),
            "last_sync_at": datetime.now(timezone.utc) - timedelta(minutes=15),
            "last_sync_status": "SUCCESS",
            "last_sync_error": None
        }
    ]

    for c in clients_data:
        in_memory_db.clients.docs.append(c)

    creatives_data = [
        # Aura Skincare
        {
            "_id": "cr_aura_1",
            "client_id": "client_aura",
            "name": "UGC - Glowing Skin Routine 30s",
            "thumbnail_url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&auto=format&fit=crop&q=80",
            "headline": "Transform Your Skin In 14 Days",
            "body_copy": "Meet the barrier repair serum dermatologists can't stop raving about. 100% vegan formula.",
            "call_to_action": "SHOP_NOW",
            "tags": ["UGC", "Video", "Scale"],
            "base_roas": 3.8,
            "base_spend": 320.0,
            "target_roas": 2.8,
            "min_spend": 150.0
        },
        {
            "_id": "cr_aura_2",
            "client_id": "client_aura",
            "name": "Founder Story - Behind the Glow",
            "thumbnail_url": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=600&auto=format&fit=crop&q=80",
            "headline": "Why I Formulated Clean Serum",
            "body_copy": "I struggled with sensitivity for 8 years until I built this calm-complex elixir.",
            "call_to_action": "LEARN_MORE",
            "tags": ["Founder", "Story"],
            "base_roas": 3.1,
            "base_spend": 240.0,
            "target_roas": 2.8,
            "min_spend": 150.0
        },
        {
            "_id": "cr_aura_3",
            "client_id": "client_aura",
            "name": "Ingredient Comparison Grid",
            "thumbnail_url": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=600&auto=format&fit=crop&q=80",
            "headline": "Us vs Them: Ingredient Transparency",
            "body_copy": "No cheap fillers. Zero parabens. Just active botanicals.",
            "call_to_action": "SHOP_NOW",
            "tags": ["Static", "Comparison"],
            "base_roas": 1.4,
            "base_spend": 180.0,
            "target_roas": 2.8,
            "min_spend": 150.0
        },
        {
            "_id": "cr_aura_4",
            "client_id": "client_aura",
            "name": "Unboxing ASMR Reel #4",
            "thumbnail_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&auto=format&fit=crop&q=80",
            "headline": "Unbox Glass Skin Perfection",
            "body_copy": "The textured unboxing experience beauty creators are obsessed with.",
            "call_to_action": "SHOP_NOW",
            "tags": ["Testing", "Reel"],
            "base_roas": 2.1,
            "base_spend": 65.0,  # Below threshold -> TESTING
            "target_roas": 2.8,
            "min_spend": 150.0
        },

        # Apex Fitness
        {
            "_id": "cr_apex_1",
            "client_id": "client_apex",
            "name": "High-Impact Seamless Leggings Demo",
            "thumbnail_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=600&auto=format&fit=crop&q=80",
            "headline": "Squat-Proof. Sweat-Wicking. Zero Roll.",
            "body_copy": "Engineered with 4-way compression fabric that moves like a second skin.",
            "call_to_action": "SHOP_NOW",
            "tags": ["Video", "Scale", "SquatProof"],
            "base_roas": 4.1,
            "base_spend": 450.0,
            "target_roas": 2.2,
            "min_spend": 100.0
        },
        {
            "_id": "cr_apex_2",
            "client_id": "client_apex",
            "name": "Try-On Haul Carousel - Restock",
            "thumbnail_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600&auto=format&fit=crop&q=80",
            "headline": "Most Requested Colors Are Back",
            "body_copy": "Midnight Navy, Sage Green, and Matte Black restocked in all sizes.",
            "call_to_action": "SHOP_NOW",
            "tags": ["Carousel", "Restock"],
            "base_roas": 2.6,
            "base_spend": 210.0,
            "target_roas": 2.2,
            "min_spend": 100.0
        },
        {
            "_id": "cr_apex_3",
            "client_id": "client_apex",
            "name": "Generic Gym Meme Graphic",
            "thumbnail_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600&auto=format&fit=crop&q=80",
            "headline": "No Days Off",
            "body_copy": "Push your limits with gear that never quits.",
            "call_to_action": "LEARN_MORE",
            "tags": ["Meme", "TopFunnel"],
            "base_roas": 0.85,
            "base_spend": 280.0,
            "target_roas": 2.2,
            "min_spend": 100.0
        },

        # Lumina Smart Home
        {
            "_id": "cr_lumina_1",
            "client_id": "client_lumina",
            "name": "Ambient Smart Lighting Night Tour",
            "thumbnail_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&auto=format&fit=crop&q=80",
            "headline": "Turn Your Room Into a Cinema",
            "body_copy": "Syncs seamlessly with Spotify, Apple TV, and voice assistants in 60 seconds.",
            "call_to_action": "SHOP_NOW",
            "tags": ["Hero", "Video", "Viral"],
            "base_roas": 4.6,
            "base_spend": 580.0,
            "target_roas": 3.2,
            "min_spend": 200.0
        },
        {
            "_id": "cr_lumina_2",
            "client_id": "client_lumina",
            "name": "Smart Blind Sunrise Automation",
            "thumbnail_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=600&auto=format&fit=crop&q=80",
            "headline": "Wake Up With Natural Sunrise",
            "body_copy": "Automate your shades based on the sun's position. Solar powered.",
            "call_to_action": "SHOP_NOW",
            "tags": ["Automation", "UGC"],
            "base_roas": 3.4,
            "base_spend": 310.0,
            "target_roas": 3.2,
            "min_spend": 200.0
        }
    ]

    today = date.today()
    dates = [(today - timedelta(days=i)).isoformat() for i in range(29, -1, -1)]

    for cr in creatives_data:
        c_doc = {
            "_id": cr["_id"],
            "client_id": cr["client_id"],
            "name": cr["name"],
            "meta_creative_id": f"meta_{cr['_id']}",
            "meta_ad_id": f"ad_{cr['_id']}",
            "thumbnail_url": cr["thumbnail_url"],
            "headline": cr["headline"],
            "body_copy": cr["body_copy"],
            "call_to_action": cr["call_to_action"],
            "status_override": None,
            "notes": "Top hook in Q3 performance tests.",
            "tags": cr["tags"],
            "first_seen_date": dates[0],
            "is_archived": False,
            "created_at": datetime.now(timezone.utc) - timedelta(days=30),
            "updated_at": datetime.now(timezone.utc)
        }
        in_memory_db.creatives.docs.append(c_doc)

        # Generate 30 daily snapshots
        past_statuses = []
        base_roas = cr["base_roas"]
        base_spend = cr["base_spend"]
        target_roas = cr["target_roas"]
        min_spend = cr["min_spend"]

        for d_str in dates:
            spend_noise = random.uniform(0.9, 1.1)
            roas_noise = random.uniform(0.92, 1.08)
            spend = round(base_spend * spend_noise, 2)
            roas = round(base_roas * roas_noise, 2)
            revenue = round(spend * roas, 2)
            purchases = max(1, int(revenue / 50)) if revenue > 0 else 0
            impressions = int(spend * 30)
            clicks = int(impressions * 0.025)
            ctr = round(clicks / impressions * 100, 2) if impressions > 0 else 0.0
            cpa = round(spend / purchases, 2) if purchases > 0 else 0.0

            status = evaluate_status(
                spend=spend,
                roas=roas,
                target_roas=target_roas,
                min_spend_threshold=min_spend
            )
            past_statuses.append(status)
            streak = calculate_streak(past_statuses)

            snap_doc = {
                "_id": f"snap_{cr['_id']}_{d_str}",
                "creative_id": cr["_id"],
                "client_id": cr["client_id"],
                "date": d_str,
                "spend": spend,
                "revenue": revenue,
                "purchases": purchases,
                "impressions": impressions,
                "clicks": clicks,
                "roas": roas,
                "ctr": ctr,
                "cpa": cpa,
                "status": status,
                "streak": streak,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            in_memory_db.daily_snapshots.docs.append(snap_doc)

    # Seed sync logs
    for c in clients_data:
        log_doc = {
            "_id": f"log_{c['_id']}",
            "client_id": c["_id"],
            "client_name": c["name"],
            "status": "SUCCESS",
            "records_synced": 3,
            "duration_ms": 640,
            "error_message": None,
            "sync_type": "SCHEDULED",
            "timestamp": datetime.now(timezone.utc) - timedelta(minutes=25)
        }
        in_memory_db.sync_logs.docs.append(log_doc)
