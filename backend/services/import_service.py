import csv
import io
import re
from datetime import datetime, timezone, date
from typing import List, Dict, Any, Optional
from bson import ObjectId

from backend.database import get_database
from backend.services.leaderboard_service import evaluate_status, calculate_streak


def clean_number(val: Any, default: float = 0.0) -> float:
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ("-", "n/a", "null", "none"):
        return default
    # Remove $, commas, %
    cleaned = re.sub(r"[^\d.-]", "", val_str)
    try:
        return float(cleaned) if cleaned else default
    except ValueError:
        return default


class ImportService:
    @staticmethod
    def parse_raw_text(raw_text: str) -> List[Dict[str, str]]:
        """
        Parses pasted CSV or TSV string into list of dicts.
        Auto-detects delimiter (tab or comma).
        """
        raw_text = raw_text.strip()
        if not raw_text:
            return []

        # Detect delimiter
        first_line = raw_text.splitlines()[0]
        delimiter = "\t" if "\t" in first_line else ","

        f = io.StringIO(raw_text)
        reader = csv.DictReader(f, delimiter=delimiter)
        
        rows = []
        for r in reader:
            # Strip whitespace from keys and values
            cleaned_row = {k.strip(): (v.strip() if v else "") for k, v in r.items() if k}
            if cleaned_row:
                rows.append(cleaned_row)
        return rows

    @staticmethod
    def map_columns(row: Dict[str, str]) -> Dict[str, Any]:
        """
        Intelligently maps varying Ads Manager column names into normalized fields.
        """
        normalized: Dict[str, Any] = {
            "name": "Untitled Creative",
            "spend": 0.0,
            "revenue": 0.0,
            "purchases": 0,
            "impressions": 0,
            "clicks": 0,
            "roas": 0.0,
            "ctr": 0.0,
            "cpa": 0.0,
            "thumbnail_url": None,
            "errors": []
        }

        # Match name
        for key, val in row.items():
            k_lower = key.lower()
            if any(term in k_lower for term in ("ad name", "creative name", "ad creative", "ad", "name")) and not normalized.get("matched_name"):
                if val:
                    normalized["name"] = val
                    normalized["matched_name"] = True

            elif any(term in k_lower for term in ("amount spent", "spend", "cost")):
                normalized["spend"] = clean_number(val)

            elif any(term in k_lower for term in ("purchase conversion value", "revenue", "conversion value", "website purchases value")):
                normalized["revenue"] = clean_number(val)

            elif any(term in k_lower for term in ("purchases", "results", "website purchases", "orders")):
                normalized["purchases"] = int(clean_number(val))

            elif any(term in k_lower for term in ("purchase roas", "roas", "return on ad spend")):
                explicit_roas = clean_number(val)
                if explicit_roas > 0:
                    normalized["explicit_roas"] = explicit_roas

            elif any(term in k_lower for term in ("impressions", "views")):
                normalized["impressions"] = int(clean_number(val))

            elif any(term in k_lower for term in ("link clicks", "clicks")):
                normalized["clicks"] = int(clean_number(val))

            elif any(term in k_lower for term in ("ctr", "click-through rate")):
                normalized["ctr"] = clean_number(val)

            elif any(term in k_lower for term in ("cpa", "cost per purchase", "cost per result")):
                normalized["cpa"] = clean_number(val)

            elif any(term in k_lower for term in ("thumbnail", "image url", "preview")):
                if val and val.startswith("http"):
                    normalized["thumbnail_url"] = val

        # Calculate derived metrics if not given
        spend = normalized["spend"]
        revenue = normalized["revenue"]
        purchases = normalized["purchases"]
        impressions = normalized["impressions"]
        clicks = normalized["clicks"]

        if normalized.get("explicit_roas"):
            normalized["roas"] = round(normalized["explicit_roas"], 2)
        else:
            normalized["roas"] = round(revenue / spend, 2) if spend > 0 else 0.0

        if normalized["ctr"] == 0.0 and impressions > 0:
            normalized["ctr"] = round(clicks / impressions * 100, 2)

        if normalized["cpa"] == 0.0 and purchases > 0:
            normalized["cpa"] = round(spend / purchases, 2)

        return normalized

    async def preview_import(
        self,
        raw_text: str,
        client_id: str
    ) -> Dict[str, Any]:
        """
        Parses text and returns preview with status tags based on client's thresholds.
        """
        target_roas = 2.5
        min_spend = 100.0

        try:
            db = get_database()
            try:
                client_doc = await db.clients.find_one({"_id": ObjectId(client_id) if ObjectId.is_valid(client_id) else client_id})
            except Exception:
                client_doc = await db.clients.find_one({"_id": client_id})

            if client_doc:
                target_roas = float(client_doc.get("target_roas", 2.5))
                min_spend = float(client_doc.get("min_spend_threshold", 100.0))
        except Exception:
            # Fallback to default thresholds if database is offline or client not yet created
            pass

        raw_rows = self.parse_raw_text(raw_text)
        if not raw_rows:
            return {"valid": False, "total_rows": 0, "rows": [], "error": "No valid tabular data detected."}

        parsed_rows = []
        for r in raw_rows:
            mapped = self.map_columns(r)
            status = evaluate_status(
                spend=mapped["spend"],
                roas=mapped["roas"],
                target_roas=target_roas,
                min_spend_threshold=min_spend
            )
            mapped["evaluated_status"] = status
            parsed_rows.append(mapped)

        return {
            "valid": True,
            "total_rows": len(parsed_rows),
            "rows": parsed_rows,
            "target_roas": target_roas,
            "min_spend_threshold": min_spend
        }

    async def commit_import(
        self,
        client_id: str,
        rows: List[Dict[str, Any]],
        target_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Persists imported rows into Creatives and DailySnapshots.
        """
        if not target_date:
            target_date = date.today().isoformat()

        db = get_database()
        try:
            client_doc = await db.clients.find_one({"_id": ObjectId(client_id) if ObjectId.is_valid(client_id) else client_id})
        except Exception:
            client_doc = await db.clients.find_one({"_id": client_id})

        if not client_doc:
            raise ValueError(f"Client {client_id} not found")

        target_roas = float(client_doc.get("target_roas", 2.5))
        min_spend = float(client_doc.get("min_spend_threshold", 100.0))

        created_count = 0
        updated_count = 0

        for r in rows:
            name = r.get("name", "Untitled Creative")
            spend = float(r.get("spend", 0.0))
            revenue = float(r.get("revenue", 0.0))
            purchases = int(r.get("purchases", 0))
            impressions = int(r.get("impressions", 0))
            clicks = int(r.get("clicks", 0))
            roas = float(r.get("roas", (revenue / spend) if spend > 0 else 0.0))
            ctr = float(r.get("ctr", (clicks / impressions * 100) if impressions > 0 else 0.0))
            cpa = float(r.get("cpa", (spend / purchases) if purchases > 0 else 0.0))
            thumbnail_url = r.get("thumbnail_url") or "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400&q=80"

            # Find existing creative by name for this client
            creative_doc = await db.creatives.find_one({
                "client_id": str(client_doc["_id"]),
                "name": name
            })

            if not creative_doc:
                creative_dict = {
                    "client_id": str(client_doc["_id"]),
                    "name": name,
                    "meta_ad_id": None,
                    "meta_creative_id": None,
                    "thumbnail_url": thumbnail_url,
                    "body_copy": None,
                    "headline": None,
                    "call_to_action": "LEARN_MORE",
                    "status_override": None,
                    "notes": "Imported via bulk paste",
                    "tags": ["Bulk Import"],
                    "first_seen_date": target_date,
                    "is_archived": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
                res = await db.creatives.insert_one(creative_dict)
                c_id = str(res.inserted_id)
                created_count += 1
            else:
                c_id = str(creative_doc["_id"])
                updated_count += 1

            status = evaluate_status(
                spend=spend,
                roas=roas,
                target_roas=target_roas,
                min_spend_threshold=min_spend
            )

            # Streak computation
            past_snapshots_cursor = db.daily_snapshots.find(
                {"creative_id": c_id, "date": {"$lt": target_date}}
            ).sort("date", 1)
            past_snapshots = await past_snapshots_cursor.to_list(length=365)
            
            historical_statuses = [
                evaluate_status(
                    spend=float(s.get("spend", 0.0)),
                    roas=float(s.get("roas", 0.0)),
                    target_roas=target_roas,
                    min_spend_threshold=min_spend
                )
                for s in past_snapshots
            ] + [status]
            streak = calculate_streak(historical_statuses)

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
                "updated_at": datetime.now(timezone.utc)
            }

            await db.daily_snapshots.update_one(
                {"creative_id": c_id, "date": target_date},
                {"$set": snapshot_data, "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
                upsert=True
            )

        return {
            "success": True,
            "total_processed": len(rows),
            "created_creatives": created_count,
            "updated_creatives": updated_count,
            "target_date": target_date
        }
