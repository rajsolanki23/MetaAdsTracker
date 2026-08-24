from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime, date, timedelta
from bson import ObjectId

from backend.database import get_database
from backend.models.client import ClientCreate, ClientUpdate, ClientSummary, ClientInDB
from backend.services.leaderboard_service import build_leaderboard_items, aggregate_client_summary

router = APIRouter(prefix="/api/clients", tags=["Clients"])


def _format_id(doc: dict) -> dict:
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.get("", response_model=List[ClientSummary])
async def list_clients():
    """
    Returns all active clients with blended performance statistics (blended ROAS, total spend, wins/losses).
    """
    db = get_database()
    today_str = date.today().isoformat()
    yesterday_str = (date.today() - timedelta(days=1)).isoformat()

    cursor = db.clients.find({"is_active": True}).sort("name", 1)
    clients = await cursor.to_list(length=100)
    
    # Fetch all creatives and snapshots for calculation
    creatives_cursor = db.creatives.find({"is_archived": False})
    all_creatives = await creatives_cursor.to_list(length=1000)

    snapshots_cursor = db.daily_snapshots.find()
    all_snapshots = await snapshots_cursor.to_list(length=10000)

    # Group snapshots by creative_id
    snapshots_by_creative = {}
    for s in all_snapshots:
        c_id = str(s.get("creative_id"))
        snapshots_by_creative.setdefault(c_id, []).append(s)

    clients_map = {str(c["_id"]): c for c in clients}

    # Build leaderboard items
    leaderboard_items = build_leaderboard_items(
        creatives=all_creatives,
        clients_map=clients_map,
        snapshots_by_creative=snapshots_by_creative,
        target_date=today_str,
        yesterday_date=yesterday_str
    )

    summaries = []
    for client in clients:
        c_id = str(client["_id"])
        client_items = [i for i in leaderboard_items if i.client_id == c_id]
        summary = aggregate_client_summary(client, client_items)
        summaries.append(summary)

    return summaries


@router.post("", response_model=ClientInDB)
async def create_client(payload: ClientCreate):
    """
    Registers a new client account with target ROAS, min spend threshold, and Meta credentials.
    """
    db = get_database()
    doc = payload.dict()
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()
    doc["last_sync_at"] = None
    doc["last_sync_status"] = None
    doc["last_sync_error"] = None

    result = await db.clients.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return ClientInDB(**doc)


@router.get("/{client_id}", response_model=ClientSummary)
async def get_client(client_id: str):
    """
    Fetches a specific client with full blended metrics.
    """
    db = get_database()
    try:
        client = await db.clients.find_one({"_id": ObjectId(client_id) if ObjectId.is_valid(client_id) else client_id})
    except Exception:
        client = await db.clients.find_one({"_id": client_id})

    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    today_str = date.today().isoformat()
    yesterday_str = (date.today() - timedelta(days=1)).isoformat()

    c_id = str(client["_id"])
    creatives = await db.creatives.find({"client_id": c_id, "is_archived": False}).to_list(length=500)
    
    snapshots_by_creative = {}
    for cr in creatives:
        cr_id = str(cr["_id"])
        snaps = await db.daily_snapshots.find({"creative_id": cr_id}).to_list(length=365)
        snapshots_by_creative[cr_id] = snaps

    clients_map = {c_id: client}
    items = build_leaderboard_items(
        creatives=creatives,
        clients_map=clients_map,
        snapshots_by_creative=snapshots_by_creative,
        target_date=today_str,
        yesterday_date=yesterday_str
    )

    summary = aggregate_client_summary(client, items)
    return summary


@router.put("/{client_id}", response_model=ClientInDB)
async def update_client(client_id: str, payload: ClientUpdate):
    """
    Updates client settings or Meta API credentials.
    """
    db = get_database()
    filter_query = {"_id": ObjectId(client_id) if ObjectId.is_valid(client_id) else client_id}
    
    update_data = {k: v for k, v in payload.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()

    await db.clients.update_one(filter_query, {"$set": update_data})
    updated = await db.clients.find_one(filter_query)
    if not updated:
        raise HTTPException(status_code=404, detail="Client not found")
    
    updated["_id"] = str(updated["_id"])
    return ClientInDB(**updated)


@router.delete("/{client_id}")
async def delete_client(client_id: str):
    """
    Soft-deletes or archives a client.
    """
    db = get_database()
    filter_query = {"_id": ObjectId(client_id) if ObjectId.is_valid(client_id) else client_id}
    res = await db.clients.update_one(filter_query, {"$set": {"is_active": False, "updated_at": datetime.utcnow()}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"status": "DELETED", "client_id": client_id}
