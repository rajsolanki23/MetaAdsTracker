import time
import logging
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional
from bson import ObjectId

from backend.database import get_database
from backend.services.meta_client import MetaClient, MetaAPIError
from backend.services.leaderboard_service import evaluate_status, calculate_streak, calculate_rank_movement

logger = logging.getLogger("sync_service")


def _extract_metric_from_actions(actions_list: Optional[List[Dict[str, Any]]], target_action: str = "purchase") -> float:
    if not actions_list:
        return 0.0
    for item in actions_list:
        action_type = item.get("action_type", "").lower()
        if target_action in action_type:
            try:
                return float(item.get("value", 0.0))
            except (ValueError, TypeError):
                return 0.0
    return 0.0


class SyncService:
    def __init__(self, meta_client: Optional[MetaClient] = None):
        self.meta_client = meta_client or MetaClient()

    async def sync_client(
        self,
        client_id: str,
        target_date: Optional[str] = None,
        sync_type: str = "MANUAL"
    ) -> Dict[str, Any]:
        """
        Synchronizes today's insights for a given client from Meta Marketing API.
        Saves immutable daily snapshots, updates streaks, and records audit logs.
        """
        start_time = time.time()
        db = get_database()
        
        # Load client from DB
        try:
            client_doc = await db.clients.find_one({"_id": ObjectId(client_id) if ObjectId.is_valid(client_id) else client_id})
        except Exception:
            client_doc = await db.clients.find_one({"_id": client_id})

        if not client_doc:
            raise ValueError(f"Client with id {client_id} not found")

        client_name = client_doc.get("name", "Unknown")
        meta_account_id = client_doc.get("meta_account_id")
        access_token = client_doc.get("access_token")
        target_roas = float(client_doc.get("target_roas", 2.5))
        min_spend = float(client_doc.get("min_spend_threshold", 100.0))

        if not target_date:
            target_date = date.today().isoformat()

        yesterday_date = (datetime.strptime(target_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")

        if not meta_account_id or not access_token:
            error_msg = "Meta Account ID or Access Token is missing"
            await self._record_sync_log(
                client_id=str(client_doc["_id"]),
                client_name=client_name,
                status="FAILED",
                records_synced=0,
                duration_ms=int((time.time() - start_time) * 1000),
                error_message=error_msg,
                sync_type=sync_type
            )
            await db.clients.update_one(
                {"_id": client_doc["_id"]},
                {"$set": {
                    "last_sync_at": datetime.utcnow(),
                    "last_sync_status": "FAILED",
                    "last_sync_error": error_msg
                }}
            )
            return {"status": "FAILED", "records_synced": 0, "error": error_msg}

        try:
            # 1. Fetch live insights & creative assets from Meta Graph API
            insights = await self.meta_client.fetch_ad_insights(
                account_id=meta_account_id,
                access_token=access_token,
                time_range={"since": target_date, "until": target_date}
            )
            
            creatives_assets = await self.meta_client.fetch_ad_creatives(
                account_id=meta_account_id,
                access_token=access_token
            )

            records_count = 0
            
            for ad_insight in insights:
                ad_id = str(ad_insight.get("ad_id"))
                ad_name = ad_insight.get("ad_name") or f"Ad {ad_id}"
                
                spend = float(ad_insight.get("spend", 0.0))
                impressions = int(ad_insight.get("impressions", 0))
                clicks = int(ad_insight.get("clicks", 0))
                
                # Purchase revenue from action_values
                action_values = ad_insight.get("action_values", [])
                revenue = _extract_metric_from_actions(action_values, "purchase")
                if revenue == 0.0:
                    revenue = _extract_metric_from_actions(action_values, "omni_purchase")
                
                # Purchases count from actions
                actions = ad_insight.get("actions", [])
                purchases = int(_extract_metric_from_actions(actions, "purchase"))
                if purchases == 0:
                    purchases = int(_extract_metric_from_actions(actions, "omni_purchase"))
                
                roas = round((revenue / spend), 2) if spend > 0 else 0.0
                ctr = round((clicks / impressions * 100), 2) if impressions > 0 else 0.0
                cpa = round((spend / purchases), 2) if purchases > 0 else 0.0

                # Creative asset metadata
                asset_meta = creatives_assets.get(ad_id, {})
                thumbnail_url = asset_meta.get("thumbnail_url")
                body_copy = asset_meta.get("body_copy")
                headline = asset_meta.get("headline")
                cta = asset_meta.get("call_to_action", "LEARN_MORE")
                meta_creative_id = asset_meta.get("creative_id")

                # Upsert / Find Creative entity
                creative_doc = await db.creatives.find_one({
                    "client_id": str(client_doc["_id"]),
                    "meta_ad_id": ad_id
                })

                if not creative_doc:
                    # New creative
                    creative_dict = {
                        "client_id": str(client_doc["_id"]),
                        "name": ad_name,
                        "meta_ad_id": ad_id,
                        "meta_creative_id": meta_creative_id,
                        "thumbnail_url": thumbnail_url or "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&q=80",
                        "body_copy": body_copy,
                        "headline": headline,
                        "call_to_action": cta,
                        "status_override": None,
                        "notes": None,
                        "tags": ["Meta Live"],
                        "first_seen_date": target_date,
                        "is_archived": False,
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                    }
                    res = await db.creatives.insert_one(creative_dict)
                    c_id = str(res.inserted_id)
                else:
                    c_id = str(creative_doc["_id"])
                    # Update thumbnail/copy if newly available
                    update_fields = {"updated_at": datetime.utcnow()}
                    if thumbnail_url and not creative_doc.get("thumbnail_url"):
                        update_fields["thumbnail_url"] = thumbnail_url
                    if body_copy and not creative_doc.get("body_copy"):
                        update_fields["body_copy"] = body_copy
                    if headline and not creative_doc.get("headline"):
                        update_fields["headline"] = headline
                    await db.creatives.update_one({"_id": creative_doc["_id"]}, {"$set": update_fields})

                # Compute Status for today
                status_override = creative_doc.get("status_override") if creative_doc else None
                status = evaluate_status(
                    spend=spend,
                    roas=roas,
                    target_roas=target_roas,
                    min_spend_threshold=min_spend,
                    status_override=status_override
                )

                # Fetch chronological historical snapshots to compute streak
                past_snapshots_cursor = db.daily_snapshots.find(
                    {"creative_id": c_id, "date": {"$lt": target_date}}
                ).sort("date", 1)
                past_snapshots = await past_snapshots_cursor.to_list(length=365)
                
                historical_statuses = [
                    evaluate_status(
                        spend=float(s.get("spend", 0.0)),
                        roas=float(s.get("roas", 0.0)),
                        target_roas=target_roas,
                        min_spend_threshold=min_spend,
                        status_override=status_override
                    )
                    for s in past_snapshots
                ] + [status]
                streak = calculate_streak(historical_statuses)

                # Upsert today's snapshot (never touches past calendar days)
                snapshot_data = {
                    "creative_id": c_id,
                    "client_id": str(client_doc["_id"]),
                    "date": target_date,
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
                    "updated_at": datetime.utcnow()
                }

                await db.daily_snapshots.update_one(
                    {"creative_id": c_id, "date": target_date},
                    {"$set": snapshot_data, "$setOnInsert": {"created_at": datetime.utcnow()}},
                    upsert=True
                )
                records_count += 1

            duration = int((time.time() - start_time) * 1000)
            
            # Update client metadata
            await db.clients.update_one(
                {"_id": client_doc["_id"]},
                {"$set": {
                    "last_sync_at": datetime.utcnow(),
                    "last_sync_status": "SUCCESS",
                    "last_sync_error": None
                }}
            )

            await self._record_sync_log(
                client_id=str(client_doc["_id"]),
                client_name=client_name,
                status="SUCCESS",
                records_synced=records_count,
                duration_ms=duration,
                error_message=None,
                sync_type=sync_type
            )

            return {
                "status": "SUCCESS",
                "client_id": str(client_doc["_id"]),
                "records_synced": records_count,
                "duration_ms": duration
            }

        except Exception as exc:
            duration = int((time.time() - start_time) * 1000)
            error_msg = str(exc)
            logger.error(f"Sync error for client {client_name}: {error_msg}")
            
            await db.clients.update_one(
                {"_id": client_doc["_id"]},
                {"$set": {
                    "last_sync_at": datetime.utcnow(),
                    "last_sync_status": "FAILED",
                    "last_sync_error": error_msg
                }}
            )
            
            await self._record_sync_log(
                client_id=str(client_doc["_id"]),
                client_name=client_name,
                status="FAILED",
                records_synced=0,
                duration_ms=duration,
                error_message=error_msg,
                sync_type=sync_type
            )
            
            return {
                "status": "FAILED",
                "client_id": str(client_doc["_id"]),
                "error": error_msg,
                "duration_ms": duration
            }

    async def sync_all_active_clients(self, sync_type: str = "SCHEDULED") -> List[Dict[str, Any]]:
        """
        Iterates and synchronizes all active client accounts.
        """
        db = get_database()
        cursor = db.clients.find({"is_active": True})
        active_clients = await cursor.to_list(length=100)
        
        results = []
        for client in active_clients:
            c_id = str(client["_id"])
            try:
                res = await self.sync_client(client_id=c_id, sync_type=sync_type)
                results.append(res)
            except Exception as e:
                results.append({"status": "FAILED", "client_id": c_id, "error": str(e)})

        return results

    async def _record_sync_log(
        self,
        client_id: Optional[str],
        client_name: Optional[str],
        status: str,
        records_synced: int,
        duration_ms: int,
        error_message: Optional[str],
        sync_type: str
    ):
        try:
            db = get_database()
            log_doc = {
                "client_id": client_id,
                "client_name": client_name,
                "status": status,
                "records_synced": records_synced,
                "duration_ms": duration_ms,
                "error_message": error_message,
                "sync_type": sync_type,
                "timestamp": datetime.utcnow()
            }
            await db.sync_logs.insert_one(log_doc)
        except Exception as e:
            logger.warning(f"Failed to record sync log: {e}")
