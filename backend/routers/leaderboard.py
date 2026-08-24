from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime, date, timedelta
from bson import ObjectId

from backend.database import get_database
from backend.models.snapshot import LeaderboardItem
from backend.services.leaderboard_service import build_leaderboard_items

router = APIRouter(prefix="/api/leaderboard", tags=["Leaderboard"])


@router.get("", response_model=List[LeaderboardItem])
async def get_leaderboard(
    client_id: Optional[str] = Query(None, description="Filter by client ID"),
    statuses: Optional[str] = Query(None, description="Comma-separated status filters: WIN,LOSS,TESTING,PAUSED"),
    target_date: Optional[str] = Query(None, description="Target date YYYY-MM-DD"),
    min_spend: Optional[float] = Query(None, ge=0.0, description="Minimum spend filter"),
    search: Optional[str] = Query(None, description="Search keyword in creative name, headline, tags"),
    sort_by: str = Query("roas", description="Metric to sort by: roas, spend, ctr, cpa, days_live, streak"),
    sort_dir: str = Query("desc", description="Sort direction: asc or desc")
):
    """
    Returns ranked ad creative leaderboard items with inline metrics, flame/ice streaks, rank movements vs yesterday, and status tags.
    """
    db = get_database()
    
    if not target_date:
        target_date = date.today().isoformat()

    yesterday_date = (datetime.strptime(target_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")

    # Fetch clients
    client_query = {"is_active": True}
    if client_id:
        try:
            client_query["_id"] = ObjectId(client_id) if ObjectId.is_valid(client_id) else client_id
        except Exception:
            client_query["_id"] = client_id
            
    clients = await db.clients.find(client_query).to_list(length=100)
    clients_map = {str(c["_id"]): c for c in clients}

    # Fetch creatives
    creatives_query = {"is_archived": False}
    if client_id:
        creatives_query["client_id"] = client_id

    creatives = await db.creatives.find(creatives_query).to_list(length=1000)
    
    # Fetch snapshots
    creative_ids = [str(c["_id"]) for c in creatives]
    snapshots = await db.daily_snapshots.find(
        {"creative_id": {"$in": creative_ids}}
    ).to_list(length=20000)

    snapshots_by_creative = {}
    for s in snapshots:
        c_id = str(s.get("creative_id"))
        snapshots_by_creative.setdefault(c_id, []).append(s)

    items = build_leaderboard_items(
        creatives=creatives,
        clients_map=clients_map,
        snapshots_by_creative=snapshots_by_creative,
        target_date=target_date,
        yesterday_date=yesterday_date,
        sort_by=sort_by,
        sort_dir=sort_dir
    )

    # Apply filters
    filtered_items = items

    # Status multi-filter
    if statuses:
        allowed_statuses = [s.strip().upper() for s in statuses.split(",") if s.strip()]
        if allowed_statuses:
            filtered_items = [i for i in filtered_items if i.status.upper() in allowed_statuses]

    # Min spend slider filter
    if min_spend is not None and min_spend > 0:
        filtered_items = [i for i in filtered_items if i.spend >= min_spend]

    # Search keyword filter
    if search:
        kw = search.strip().lower()
        filtered_items = [
            i for i in filtered_items
            if (kw in i.name.lower())
            or (i.headline and kw in i.headline.lower())
            or (i.client_name and kw in i.client_name.lower())
            or any(kw in tag.lower() for tag in i.tags)
        ]

    return filtered_items


@router.get("/podium", response_model=List[LeaderboardItem])
async def get_podium_top3(
    client_id: Optional[str] = Query(None, description="Filter podium by client ID"),
    target_date: Optional[str] = Query(None, description="Target date YYYY-MM-DD")
):
    """
    Returns the top 3 highest-ranking winning creatives for the game leaderboard podium.
    """
    items = await get_leaderboard(
        client_id=client_id,
        target_date=target_date,
        sort_by="roas",
        sort_dir="desc"
    )
    return items[:3]
