import httpx
import logging
import asyncio
from typing import Dict, Any, Optional, List
from backend.config import settings

logger = logging.getLogger("meta_client")

class MetaAPIError(Exception):
    def __init__(self, message: str, status_code: int = 400, fbtrace_id: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.fbtrace_id = fbtrace_id


class MetaClient:
    """
    Async client for Meta Marketing Graph API v18.0.
    Handles authentication, rate limit backoff, pagination, and error formatting.
    """
    def __init__(self, base_url: Optional[str] = None, api_version: Optional[str] = None):
        self.api_version = api_version or settings.META_GRAPH_API_VERSION
        self.base_url = (base_url or settings.META_GRAPH_API_BASE_URL).rstrip("/")
        self.timeout = httpx.Timeout(connect=10.0, read=30.0, write=10.0, pool=10.0)

    def _normalize_account_id(self, account_id: str) -> str:
        account_id = account_id.strip()
        if not account_id.startswith("act_"):
            return f"act_{account_id}"
        return account_id

    async def _request(
        self,
        method: str,
        path: str,
        access_token: str,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{self.api_version}/{path.lstrip('/')}"
        query_params = {"access_token": access_token}
        if params:
            query_params.update(params)

        attempt = 0
        backoff = 1.0

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while attempt < max_retries:
                attempt += 1
                try:
                    logger.debug(f"Meta API {method} {url} (attempt {attempt})")
                    response = await client.request(method=method, url=url, params=query_params)
                    
                    # Inspect rate limit headers if present
                    rate_limit = response.headers.get("x-business-use-case-usage") or response.headers.get("x-ad-account-usage")
                    if rate_limit:
                        logger.debug(f"Meta rate limit status: {rate_limit}")

                    if response.status_code == 200:
                        return response.json()

                    error_data = {}
                    try:
                        error_data = response.json().get("error", {})
                    except Exception:
                        pass

                    error_message = error_data.get("message", response.text)
                    error_code = error_data.get("code")
                    fbtrace_id = error_data.get("fbtrace_id")

                    # Handle transient rate limit / server errors with backoff
                    if response.status_code in (429, 500, 502, 503, 504) or error_code in (17, 32, 613):
                        logger.warning(f"Meta API transient error ({response.status_code}): {error_message}. Retrying in {backoff}s...")
                        await asyncio.sleep(backoff)
                        backoff *= 2
                        continue

                    # Non-retryable error (e.g. 401 Invalid Token, 403 Permission Denied)
                    raise MetaAPIError(
                        message=f"Meta API Error: {error_message} (code {error_code})",
                        status_code=response.status_code,
                        fbtrace_id=fbtrace_id
                    )

                except httpx.RequestError as exc:
                    logger.warning(f"Network error calling Meta API: {exc}. Retrying in {backoff}s...")
                    if attempt >= max_retries:
                        raise MetaAPIError(f"Network connection failed: {str(exc)}", status_code=503)
                    await asyncio.sleep(backoff)
                    backoff *= 2

        raise MetaAPIError("Exceeded maximum retries calling Meta API", status_code=500)

    async def test_connection(self, account_id: str, access_token: str) -> Dict[str, Any]:
        """
        Validates token and account access by fetching ad account details.
        """
        clean_id = self._normalize_account_id(account_id)
        params = {
            "fields": "id,name,account_status,currency,timezone_name,amount_spent,business_name"
        }
        res = await self._request("GET", clean_id, access_token=access_token, params=params)
        return {
            "valid": True,
            "account_id": res.get("id"),
            "account_name": res.get("name"),
            "business_name": res.get("business_name"),
            "currency": res.get("currency", "USD"),
            "timezone": res.get("timezone_name", "America/New_York"),
            "account_status": res.get("account_status"),
        }

    async def fetch_ad_insights(
        self,
        account_id: str,
        access_token: str,
        date_preset: str = "today",
        time_range: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetches creative/ad-level performance insights including spend, purchase value (ROAS), clicks, impressions.
        """
        clean_id = self._normalize_account_id(account_id)
        params: Dict[str, Any] = {
            "level": "ad",
            "fields": (
                "ad_id,ad_name,adset_name,campaign_name,spend,impressions,clicks,ctr,cpc,cpm,"
                "actions,action_values,cost_per_action_type,date_start,date_stop"
            ),
            "limit": 250
        }
        if time_range:
            params["time_range"] = str(time_range).replace("'", '"')
        else:
            params["date_preset"] = date_preset

        all_records: List[Dict[str, Any]] = []
        path = f"{clean_id}/insights"

        res = await self._request("GET", path, access_token=access_token, params=params)
        data = res.get("data", [])
        all_records.extend(data)

        # Handle pagination if more than 250 ads
        paging = res.get("paging", {})
        while "next" in paging and len(all_records) < 1000:
            next_url = paging["next"]
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.get(next_url)
                if resp.status_code == 200:
                    page_data = resp.json()
                    all_records.extend(page_data.get("data", []))
                    paging = page_data.get("paging", {})
                else:
                    break

        return all_records

    async def fetch_ad_creatives(
        self,
        account_id: str,
        access_token: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetches ad creative metadata (preview thumbnail, copy text, headline, CTA) keyed by ad_id.
        """
        clean_id = self._normalize_account_id(account_id)
        params = {
            "fields": (
                "id,name,creative{id,name,thumbnail_url,image_url,title,body,call_to_action_type,"
                "object_story_spec{link_data{message,name,call_to_action,picture,image_hash}}}"
            ),
            "limit": 250
        }
        creatives_map: Dict[str, Dict[str, Any]] = {}
        try:
            res = await self._request("GET", f"{clean_id}/ads", access_token=access_token, params=params)
            for ad in res.get("data", []):
                ad_id = ad.get("id")
                creative_obj = ad.get("creative", {})
                
                # Extract image thumbnail
                thumbnail_url = creative_obj.get("thumbnail_url") or creative_obj.get("image_url")
                body = creative_obj.get("body")
                title = creative_obj.get("title")
                cta = creative_obj.get("call_to_action_type", "LEARN_MORE")
                
                # Fallback to object_story_spec if available
                story_spec = creative_obj.get("object_story_spec", {}).get("link_data", {})
                if story_spec:
                    thumbnail_url = thumbnail_url or story_spec.get("picture")
                    body = body or story_spec.get("message")
                    title = title or story_spec.get("name")
                    if story_spec.get("call_to_action"):
                        cta = story_spec.get("call_to_action", {}).get("type", cta)
                        
                creatives_map[ad_id] = {
                    "ad_name": ad.get("name"),
                    "creative_id": creative_obj.get("id"),
                    "thumbnail_url": thumbnail_url,
                    "body_copy": body,
                    "headline": title,
                    "call_to_action": cta
                }
        except Exception as e:
            logger.warning(f"Failed to fetch ad creative assets: {e}")

        return creatives_map
