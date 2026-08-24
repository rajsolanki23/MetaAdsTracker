from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from backend.models.client import ClientInDB, ClientSummary
from backend.models.creative import CreativeInDB
from backend.models.snapshot import DailySnapshotInDB, LeaderboardItem


def evaluate_status(
    spend: float,
    roas: float,
    target_roas: float,
    min_spend_threshold: float,
    status_override: Optional[str] = None
) -> str:
    """
    Evaluates creative status based on performance thresholds:
    - PAUSED: If explicitly overridden or paused
    - TESTING: If spend is below client minimum spend threshold
    - WIN: If ROAS >= client target ROAS
    - LOSS: If ROAS < client target ROAS and spend >= threshold
    """
    if status_override:
        return status_override.upper()
    
    if spend < min_spend_threshold:
        return "TESTING"
    
    if roas >= target_roas:
        return "WIN"
    else:
        return "LOSS"


def calculate_streak(chronological_statuses: List[str]) -> int:
    """
    Calculates consecutive streak from a list of statuses ordered from oldest to newest:
    - Positive integer (+N) for consecutive WIN days (flame 🔥)
    - Negative integer (-N) for consecutive LOSS days (ice ❄️)
    - 0 for TESTING / PAUSED or no history
    """
    if not chronological_statuses:
        return 0
    
    latest_status = chronological_statuses[-1]
    if latest_status not in ("WIN", "LOSS"):
        return 0
    
    streak_count = 0
    for s in reversed(chronological_statuses):
        if s == latest_status:
            streak_count += 1
        else:
            break
            
    return streak_count if latest_status == "WIN" else -streak_count


def calculate_rank_movement(
    today_rank: int,
    yesterday_rank: Optional[int]
) -> Tuple[str, int]:
    """
    Compares today's rank with yesterday's rank:
    - Returns (movement_code, delta_val)
    - Examples: ("UP_2", 2), ("DOWN_1", -1), ("SAME", 0), ("NEW", 0)
    """
    if yesterday_rank is None:
        return ("NEW", 0)
    
    if today_rank < yesterday_rank:
        delta = yesterday_rank - today_rank
        return (f"UP_{delta}", delta)
    elif today_rank > yesterday_rank:
        delta = today_rank - yesterday_rank
        return (f"DOWN_{delta}", -delta)
    else:
        return ("SAME", 0)


def build_leaderboard_items(
    creatives: List[Dict],
    clients_map: Dict[str, Dict],
    snapshots_by_creative: Dict[str, List[Dict]],
    target_date: str,
    yesterday_date: str,
    sort_by: str = "roas",
    sort_dir: str = "desc"
) -> List[LeaderboardItem]:
    """
    Builds and ranks LeaderboardItems for a given date.
    Calculates immutable rank movement vs yesterday and continuous streaks.
    """
    items: List[LeaderboardItem] = []
    
    for creative in creatives:
        c_id = str(creative["_id"])
        client_id = str(creative["client_id"])
        client = clients_map.get(client_id, {})
        
        target_roas = float(client.get("target_roas", 2.5))
        min_spend = float(client.get("min_spend_threshold", 100.0))
        client_name = client.get("name", "Unknown Client")
        
        c_snapshots = snapshots_by_creative.get(c_id, [])
        # Sort snapshots by date ascending
        c_snapshots_sorted = sorted(c_snapshots, key=lambda s: s.get("date", ""))
        
        # Find today's snapshot and yesterday's snapshot
        today_snap = next((s for s in c_snapshots_sorted if s.get("date") == target_date), None)
        yesterday_snap = next((s for s in c_snapshots_sorted if s.get("date") == yesterday_date), None)
        
        if today_snap:
            spend = float(today_snap.get("spend", 0.0))
            revenue = float(today_snap.get("revenue", 0.0))
            purchases = int(today_snap.get("purchases", 0))
            impressions = int(today_snap.get("impressions", 0))
            clicks = int(today_snap.get("clicks", 0))
            roas = float(today_snap.get("roas", (revenue / spend) if spend > 0 else 0.0))
            ctr = float(today_snap.get("ctr", (clicks / impressions * 100) if impressions > 0 else 0.0))
            cpa = float(today_snap.get("cpa", (spend / purchases) if purchases > 0 else 0.0))
        else:
            # Aggregate or zero fallback
            spend = 0.0
            revenue = 0.0
            purchases = 0
            impressions = 0
            clicks = 0
            roas = 0.0
            ctr = 0.0
            cpa = 0.0

        # Evaluate status
        status = evaluate_status(
            spend=spend,
            roas=roas,
            target_roas=target_roas,
            min_spend_threshold=min_spend,
            status_override=creative.get("status_override")
        )
        
        # Calculate streak using chronological history up to today
        historical_statuses = [
            evaluate_status(
                spend=float(s.get("spend", 0.0)),
                roas=float(s.get("roas", 0.0)),
                target_roas=target_roas,
                min_spend_threshold=min_spend,
                status_override=creative.get("status_override")
            )
            for s in c_snapshots_sorted if s.get("date", "") <= target_date
        ]
        streak = calculate_streak(historical_statuses)
        
        # Calculate days live
        first_seen = creative.get("first_seen_date", target_date)
        try:
            d1 = datetime.strptime(first_seen, "%Y-%m-%d")
            d2 = datetime.strptime(target_date, "%Y-%m-%d")
            days_live = max(1, (d2 - d1).days + 1)
        except Exception:
            days_live = 1

        yesterday_rank = yesterday_snap.get("rank") if yesterday_snap else None
        
        item = LeaderboardItem(
            id=c_id,
            name=creative.get("name", "Untitled Ad"),
            thumbnail_url=creative.get("thumbnail_url"),
            client_id=client_id,
            client_name=client_name,
            target_roas=target_roas,
            min_spend_threshold=min_spend,
            spend=spend,
            revenue=revenue,
            purchases=purchases,
            impressions=impressions,
            clicks=clicks,
            roas=roas,
            ctr=ctr,
            cpa=cpa,
            days_live=days_live,
            status=status,
            streak=streak,
            rank=0,  # assigned after sorting
            yesterday_rank=yesterday_rank,
            rank_movement="NEW",
            rank_movement_val=0,
            first_seen_date=first_seen,
            headline=creative.get("headline"),
            body_copy=creative.get("body_copy"),
            tags=creative.get("tags", []),
            notes=creative.get("notes")
        )
        items.append(item)
    
    # Sort items by requested metric (default ROAS desc)
    reverse = (sort_dir.lower() == "desc")
    if sort_by == "roas":
        items.sort(key=lambda x: (x.roas, x.spend), reverse=reverse)
    elif sort_by == "spend":
        items.sort(key=lambda x: x.spend, reverse=reverse)
    elif sort_by == "ctr":
        items.sort(key=lambda x: x.ctr, reverse=reverse)
    elif sort_by == "cpa":
        # For CPA lower is better when ascending, handle 0
        items.sort(key=lambda x: (x.cpa if x.cpa > 0 else 999999), reverse=reverse)
    elif sort_by == "days_live":
        items.sort(key=lambda x: x.days_live, reverse=reverse)
    elif sort_by == "streak":
        items.sort(key=lambda x: x.streak, reverse=reverse)
    else:
        items.sort(key=lambda x: (x.roas, x.spend), reverse=reverse)
        
    # Assign ranks and calculate rank movement
    for idx, item in enumerate(items, start=1):
        item.rank = idx
        movement_code, delta = calculate_rank_movement(idx, item.yesterday_rank)
        item.rank_movement = movement_code
        item.rank_movement_val = delta
        
    return items


def aggregate_client_summary(
    client: Dict,
    client_leaderboard_items: List[LeaderboardItem]
) -> ClientSummary:
    """
    Computes blended metrics, win/loss/testing counts, and best/worst creative for a client.
    """
    c_id = str(client["_id"])
    target_roas = float(client.get("target_roas", 2.5))
    
    total_spend = sum(i.spend for i in client_leaderboard_items)
    total_rev = sum(i.revenue for i in client_leaderboard_items)
    blended_roas = (total_rev / total_spend) if total_spend > 0 else 0.0
    
    wins = sum(1 for i in client_leaderboard_items if i.status == "WIN")
    losses = sum(1 for i in client_leaderboard_items if i.status == "LOSS")
    testing = sum(1 for i in client_leaderboard_items if i.status == "TESTING")
    paused = sum(1 for i in client_leaderboard_items if i.status == "PAUSED")
    
    # Best creative (highest ROAS with spend > 0)
    spenders = [i for i in client_leaderboard_items if i.spend > 0]
    best_c = max(spenders, key=lambda i: i.roas) if spenders else None
    
    # Worst creative (lowest ROAS with spend >= min_spend_threshold)
    min_spend = float(client.get("min_spend_threshold", 100.0))
    threshold_spenders = [i for i in client_leaderboard_items if i.spend >= min_spend]
    worst_c = min(threshold_spenders, key=lambda i: i.roas) if threshold_spenders else None
    
    # Health status evaluation
    if blended_roas >= target_roas:
        health_status = "HEALTHY"
    elif blended_roas >= (target_roas * 0.75):
        health_status = "WARNING"
    else:
        health_status = "CRITICAL"
        
    return ClientSummary(
        _id=c_id,
        name=client.get("name", ""),
        meta_account_id=client.get("meta_account_id"),
        access_token=client.get("access_token"),
        target_roas=target_roas,
        min_spend_threshold=min_spend,
        currency=client.get("currency", "USD"),
        timezone=client.get("timezone", "America/New_York"),
        is_active=client.get("is_active", True),
        created_at=client.get("created_at", datetime.utcnow()),
        updated_at=client.get("updated_at", datetime.utcnow()),
        last_sync_at=client.get("last_sync_at"),
        last_sync_status=client.get("last_sync_status"),
        last_sync_error=client.get("last_sync_error"),
        blended_spend=round(total_spend, 2),
        blended_revenue=round(total_rev, 2),
        blended_roas=round(blended_roas, 2),
        active_creatives_count=len(client_leaderboard_items),
        wins_count=wins,
        losses_count=losses,
        testing_count=testing,
        paused_count=paused,
        best_creative_name=best_c.name if best_c else None,
        best_creative_roas=best_c.roas if best_c else None,
        worst_creative_name=worst_c.name if worst_c else None,
        worst_creative_roas=worst_c.roas if worst_c else None,
        health_status=health_status
    )
