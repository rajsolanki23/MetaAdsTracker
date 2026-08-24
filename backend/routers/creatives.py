from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from bson import ObjectId

from backend.database import get_database
from backend.models.creative import CreativeCreate, CreativeUpdate, CreativeInDB
from backend.models.snapshot import DailySnapshotInDB

router = APIRouter(prefix="/api/creatives", tags=["Creatives"])


@router.get("/{creative_id}", response_model=CreativeInDB)
async def get_creative(creative_id: str):
    """
    Returns creative entity details (headline, body copy, tags, notes, status override).
    """
    db = get_database()
    try:
        doc = await db.creatives.find_one({"_id": ObjectId(creative_id) if ObjectId.is_valid(creative_id) else creative_id})
    except Exception:
        doc = await db.creatives.find_one({"_id": creative_id})

    if not doc:
        raise HTTPException(status_code=404, detail="Creative not found")
    
    doc["_id"] = str(doc["_id"])
    return CreativeInDB(**doc)


@router.post("", response_model=CreativeInDB)
async def create_creative(payload: CreativeCreate):
    """
    Manually creates a new creative entry.
    """
    db = get_database()
    doc = payload.dict()
    doc["first_seen_date"] = date.today().isoformat()
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()

    res = await db.creatives.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    return CreativeInDB(**doc)


@router.put("/{creative_id}", response_model=CreativeInDB)
async def update_creative(creative_id: str, payload: CreativeUpdate):
    """
    Updates creative metadata (notes, status override, tags, headline, copy).
    """
    db = get_database()
    filter_query = {"_id": ObjectId(creative_id) if ObjectId.is_valid(creative_id) else creative_id}
    
    update_data = {k: v for k, v in payload.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    await db.creatives.update_one(filter_query, {"$set": update_data})
    updated = await db.creatives.find_one(filter_query)
    if not updated:
        raise HTTPException(status_code=404, detail="Creative not found")
    
    updated["_id"] = str(updated["_id"])
    return CreativeInDB(**updated)


@router.get("/{creative_id}/snapshots", response_model=List[DailySnapshotInDB])
async def get_creative_snapshots(
    creative_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve")
):
    """
    Returns historical daily performance snapshots for a creative.
    """
    db = get_database()
    cursor = db.daily_snapshots.find({"creative_id": creative_id}).sort("date", -1).limit(days)
    docs = await cursor.to_list(length=days)
    
    results = []
    for d in docs:
        d["_id"] = str(d["_id"])
        results.append(DailySnapshotInDB(**d))
    return results


@router.get("/{creative_id}/trend")
async def get_creative_trend(
    creative_id: str,
    days: int = Query(30, ge=7, le=90, description="Days of trend history")
):
    """
    Returns time-series trendline data tailored for Recharts visualization.
    """
    db = get_database()
    # Fetch creative to obtain client_id and target_roas
    try:
        creative = await db.creatives.find_one({"_id": ObjectId(creative_id) if ObjectId.is_valid(creative_id) else creative_id})
    except Exception:
        creative = await db.creatives.find_one({"_id": creative_id})

    if not creative:
        raise HTTPException(status_code=404, detail="Creative not found")

    client_id = str(creative.get("client_id"))
    try:
        client = await db.clients.find_one({"_id": ObjectId(client_id) if ObjectId.is_valid(client_id) else client_id})
    except Exception:
        client = await db.clients.find_one({"_id": client_id})

    target_roas = float(client.get("target_roas", 2.5)) if client else 2.5

    # Fetch snapshots sorted chronologically (oldest to newest)
    cursor = db.daily_snapshots.find({"creative_id": creative_id}).sort("date", 1)
    snapshots = await cursor.to_list(length=days)

    trend_points = []
    for s in snapshots:
        trend_points.append({
            "date": s.get("date"),
            "spend": float(s.get("spend", 0.0)),
            "revenue": float(s.get("revenue", 0.0)),
            "roas": float(s.get("roas", 0.0)),
            "cpa": float(s.get("cpa", 0.0)),
            "ctr": float(s.get("ctr", 0.0)),
            "target_roas": target_roas,
            "status": s.get("status", "TESTING"),
            "streak": s.get("streak", 0)
        })

    return {
        "creative_id": creative_id,
        "creative_name": creative.get("name"),
        "target_roas": target_roas,
        "data_points": trend_points
    }
