import asyncio
import random
from datetime import datetime, date, timedelta, timezone
from backend.database import get_database, connect_to_mongo, close_mongo_connection
from backend.services.leaderboard_service import evaluate_status, calculate_streak

CLIENTS_DATA = [
    {
        "name": "Aura Skincare",
        "meta_account_id": "act_849201948",
        "access_token": "EAABdemo_token_aura_skincare_live",
        "target_roas": 2.8,
        "min_spend_threshold": 150.0,
        "currency": "USD",
        "timezone": "America/New_York",
        "is_active": True
    },
    {
        "name": "Apex Fitness Apparel",
        "meta_account_id": "act_573829104",
        "access_token": "EAABdemo_token_apex_fitness_live",
        "target_roas": 2.2,
        "min_spend_threshold": 100.0,
        "currency": "USD",
        "timezone": "America/Chicago",
        "is_active": True
    },
    {
        "name": "Lumina Smart Home",
        "meta_account_id": "act_392817402",
        "access_token": "EAABdemo_token_lumina_home_live",
        "target_roas": 3.2,
        "min_spend_threshold": 200.0,
        "currency": "USD",
        "timezone": "America/Los_Angeles",
        "is_active": True
    }
]

CREATIVES_TEMPLATES = [
    # Aura Skincare
    {
        "client_name": "Aura Skincare",
        "name": "UGC - Glowing Skin Routine 30s",
        "thumbnail_url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&auto=format&fit=crop&q=80",
        "headline": "Transform Your Skin In 14 Days",
        "body_copy": "Meet the barrier repair serum dermatologists can't stop raving about. 100% vegan formula.",
        "call_to_action": "SHOP_NOW",
        "tags": ["UGC", "Video", "Founder Favorite"],
        "base_roas": 3.8,
        "base_spend": 320.0,
        "is_winner": True
    },
    {
        "client_name": "Aura Skincare",
        "name": "Founder Story - Behind the Glow",
        "thumbnail_url": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=600&auto=format&fit=crop&q=80",
        "headline": "Why I Quit My Job to Fix Sensitive Skin",
        "body_copy": "I struggled with redness for 8 years until I formulated this calm-complex elixir.",
        "call_to_action": "LEARN_MORE",
        "tags": ["Founder", "Brand Story"],
        "base_roas": 3.1,
        "base_spend": 240.0,
        "is_winner": True
    },
    {
        "client_name": "Aura Skincare",
        "name": "Comparison Grid vs Competitors",
        "thumbnail_url": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=600&auto=format&fit=crop&q=80",
        "headline": "Us vs Them: Look at the Ingredients",
        "body_copy": "No cheap fillers. Zero parabens. Just active botanicals that actually penetrate.",
        "call_to_action": "SHOP_NOW",
        "tags": ["Static", "Comparison"],
        "base_roas": 1.4,
        "base_spend": 180.0,
        "is_winner": False
    },
    {
        "client_name": "Aura Skincare",
        "name": "Unboxing ASMR Reel Test #4",
        "thumbnail_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&auto=format&fit=crop&q=80",
        "headline": "Unbox Glass Skin Perfection",
        "body_copy": "The textured unboxing experience beauty creators are obsessed with.",
        "call_to_action": "SHOP_NOW",
        "tags": ["Testing", "Reel"],
        "base_roas": 2.1,
        "base_spend": 65.0,  # Below threshold -> TESTING
        "is_winner": False
    },
    {
        "client_name": "Aura Skincare",
        "name": "Old Summer Promo Banner (Paused)",
        "thumbnail_url": "https://images.unsplash.com/photo-1512290900672-1f5be4f2d37c?w=600&auto=format&fit=crop&q=80",
        "headline": "Summer Splash 20% Off",
        "body_copy": "Limited edition glow bundle before stock runs out.",
        "call_to_action": "SHOP_NOW",
        "tags": ["Promo", "Seasonal"],
        "base_roas": 0.9,
        "base_spend": 0.0,
        "status_override": "PAUSED",
        "is_winner": False
    },

    # Apex Fitness
    {
        "client_name": "Apex Fitness Apparel",
        "name": "High-Impact Seamless Leggings Demo",
        "thumbnail_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=600&auto=format&fit=crop&q=80",
        "headline": "Squat-Proof. Sweat-Wicking. Zero Roll.",
        "body_copy": "Engineered with 4-way compression fabric that moves like a second skin.",
        "call_to_action": "SHOP_NOW",
        "tags": ["Video", "Squat-Proof", "Scale"],
        "base_roas": 4.1,
        "base_spend": 450.0,
        "is_winner": True
    },
    {
        "client_name": "Apex Fitness Apparel",
        "name": "Gym Hook - Try-On Haul Carousel",
        "thumbnail_url": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600&auto=format&fit=crop&q=80",
        "headline": "Our Most Requested Colors Are Back",
        "body_copy": "Midnight Navy, Sage Green, and Matte Black restocked in all sizes.",
        "call_to_action": "SHOP_NOW",
        "tags": ["Carousel", "Restock"],
        "base_roas": 2.6,
        "base_spend": 210.0,
        "is_winner": True
    },
    {
        "client_name": "Apex Fitness Apparel",
        "name": "Generic Gym Motivation Meme",
        "thumbnail_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600&auto=format&fit=crop&q=80",
        "headline": "No Days Off",
        "body_copy": "Push your limits with gear that never quits.",
        "call_to_action": "LEARN_MORE",
        "tags": ["Meme", "Top of Funnel"],
        "base_roas": 0.85,
        "base_spend": 280.0,
        "is_winner": False
    },
    {
        "client_name": "Apex Fitness Apparel",
        "name": "New Drop: Compression Shorts V2",
        "thumbnail_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=600&auto=format&fit=crop&q=80",
        "headline": "Built for Heavy Lifts",
        "body_copy": "Dual layer phone pockets with reinforced waistband.",
        "call_to_action": "SHOP_NOW",
        "tags": ["Testing", "Shorts"],
        "base_roas": 1.9,
        "base_spend": 45.0,  # TESTING
        "is_winner": False
    },

    # Lumina Smart Home
    {
        "client_name": "Lumina Smart Home",
        "name": "Ambient Smart Lighting Night Tour",
        "thumbnail_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&auto=format&fit=crop&q=80",
        "headline": "Turn Your Room Into a Cinema",
        "body_copy": "Syncs seamlessly with Spotify, Apple TV, and voice assistants in under 60 seconds.",
        "call_to_action": "SHOP_NOW",
        "tags": ["Hero", "Video", "Viral"],
        "base_roas": 4.6,
        "base_spend": 580.0,
        "is_winner": True
    },
    {
        "client_name": "Lumina Smart Home",
        "name": "Smart Blind Automation Setup 15s",
        "thumbnail_url": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=600&auto=format&fit=crop&q=80",
        "headline": "Wake Up With Natural Sunrise",
        "body_copy": "Automate your shades based on the sun's position. Solar powered.",
        "call_to_action": "SHOP_NOW",
        "tags": ["Automation", "UGC"],
        "base_roas": 3.4,
        "base_spend": 310.0,
        "is_winner": True
    },
    {
        "client_name": "Lumina Smart Home",
        "name": "Technical Spec Infographic",
        "thumbnail_url": "https://images.unsplash.com/photo-1558002038-1055907df827?w=600&auto=format&fit=crop&q=80",
        "headline": "Matter & Zigbee Compatible",
        "body_copy": "The only bridge you'll ever need for your entire smart home ecosystem.",
        "call_to_action": "LEARN_MORE",
        "tags": ["Infographic", "Specs"],
        "base_roas": 1.2,
        "base_spend": 320.0,
        "is_winner": False
    },
    {
        "client_name": "Lumina Smart Home",
        "name": "Door Sensor Micro-Ad Hook #2",
        "thumbnail_url": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=600&auto=format&fit=crop&q=80",
        "headline": "Never Wonder If You Locked Up",
        "body_copy": "Instant alerts on your phone whenever any door or window opens.",
        "call_to_action": "SHOP_NOW",
        "tags": ["Testing", "Security"],
        "base_roas": 2.5,
        "base_spend": 80.0,  # TESTING
        "is_winner": False
    }
]


async def seed_database():
    print("[INIT] Connecting to database for seeding demo data...")
    await connect_to_mongo()
    db = get_database()

    # Clear existing demo data
    print("[CLEAN] Cleaning up old collections...")
    await db.clients.delete_many({})
    await db.creatives.delete_many({})
    await db.daily_snapshots.delete_many({})
    await db.sync_logs.delete_many({})

    print("[CLIENTS] Seeding Clients...")
    client_ids = {}
    for c_data in CLIENTS_DATA:
        c_doc = {
            **c_data,
            "created_at": datetime.now(timezone.utc) - timedelta(days=35),
            "updated_at": datetime.now(timezone.utc),
            "last_sync_at": datetime.now(timezone.utc) - timedelta(minutes=25),
            "last_sync_status": "SUCCESS",
            "last_sync_error": None
        }
        res = await db.clients.insert_one(c_doc)
        client_ids[c_data["name"]] = str(res.inserted_id)

    today = date.today()
    days_history = 30
    dates = [(today - timedelta(days=i)).isoformat() for i in range(days_history - 1, -1, -1)]

    print(f"[CREATIVES] Seeding {len(CREATIVES_TEMPLATES)} Creatives across 30 days of immutable snapshots...")

    for template in CREATIVES_TEMPLATES:
        client_name = template["client_name"]
        client_id = client_ids[client_name]
        client_info = next(c for c in CLIENTS_DATA if c["name"] == client_name)
        target_roas = client_info["target_roas"]
        min_spend = client_info["min_spend_threshold"]

        first_seen = dates[0] if template.get("base_spend", 0) > 100 else dates[-5]

        creative_doc = {
            "client_id": client_id,
            "name": template["name"],
            "meta_creative_id": f"cr_{random.randint(100000, 999999)}",
            "meta_ad_id": f"ad_{random.randint(10000000, 99999999)}",
            "thumbnail_url": template["thumbnail_url"],
            "headline": template["headline"],
            "body_copy": template["body_copy"],
            "call_to_action": template.get("call_to_action", "LEARN_MORE"),
            "status_override": template.get("status_override"),
            "notes": "Top performing hook in Q3 test cycle" if template.get("is_winner") else "Fatigued hook, evaluate revision",
            "tags": template.get("tags", []),
            "first_seen_date": first_seen,
            "is_archived": False,
            "created_at": datetime.now(timezone.utc) - timedelta(days=32),
            "updated_at": datetime.now(timezone.utc)
        }
        res = await db.creatives.insert_one(creative_doc)
        creative_id = str(res.inserted_id)

        # Generate 30 daily snapshots
        base_roas = template["base_roas"]
        base_spend = template["base_spend"]

        past_statuses = []

        for d_str in dates:
            if d_str < first_seen:
                continue

            # Add gentle variance to simulate real advertising data
            spend_noise = random.uniform(0.85, 1.15)
            spend = round(base_spend * spend_noise, 2)
            
            if template.get("status_override") == "PAUSED":
                spend = 0.0
                revenue = 0.0
                roas = 0.0
                purchases = 0
                clicks = 0
                impressions = 0
            else:
                roas_noise = random.uniform(0.9, 1.1)
                roas = round(base_roas * roas_noise, 2)
                revenue = round(spend * roas, 2)
                cpa = round(spend / (max(1, int(revenue / 45))), 2)
                purchases = max(1, int(revenue / 45)) if revenue > 0 else 0
                impressions = int(spend * random.randint(25, 40))
                clicks = int(impressions * (random.uniform(0.015, 0.035)))

            ctr = round(clicks / impressions * 100, 2) if impressions > 0 else 0.0
            computed_cpa = round(spend / purchases, 2) if purchases > 0 else 0.0

            status = evaluate_status(
                spend=spend,
                roas=roas,
                target_roas=target_roas,
                min_spend_threshold=min_spend,
                status_override=template.get("status_override")
            )
            past_statuses.append(status)
            streak = calculate_streak(past_statuses)

            snapshot_doc = {
                "creative_id": creative_id,
                "client_id": client_id,
                "date": d_str,
                "spend": spend,
                "revenue": revenue,
                "purchases": purchases,
                "impressions": impressions,
                "clicks": clicks,
                "roas": roas,
                "ctr": ctr,
                "cpa": computed_cpa,
                "status": status,
                "streak": streak,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            await db.daily_snapshots.insert_one(snapshot_doc)

    # Seed initial sync log
    print("[LOGS] Seeding Sync Audit Logs...")
    for name, c_id in client_ids.items():
        log_doc = {
            "client_id": c_id,
            "client_name": name,
            "status": "SUCCESS",
            "records_synced": 4,
            "duration_ms": random.randint(420, 890),
            "error_message": None,
            "sync_type": "SCHEDULED",
            "timestamp": datetime.now(timezone.utc) - timedelta(minutes=random.randint(15, 120))
        }
        await db.sync_logs.insert_one(log_doc)

    print("[SUCCESS] Demo database seeding complete! 3 Clients, 13 Creatives, ~300 Immutable Snapshots created.")
    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(seed_database())
