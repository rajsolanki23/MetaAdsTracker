import pytest
from unittest.mock import AsyncMock, patch
from backend.services.meta_client import MetaClient
from backend.services.sync_service import _extract_metric_from_actions


def test_extract_metric_from_actions():
    actions = [
        {"action_type": "link_click", "value": "150"},
        {"action_type": "offsite_conversion.fb_pixel_purchase", "value": "1250.50"},
        {"action_type": "post_engagement", "value": "300"}
    ]
    val = _extract_metric_from_actions(actions, "purchase")
    assert val == 1250.50

    # No match returns 0.0
    val_none = _extract_metric_from_actions(actions, "app_install")
    assert val_none == 0.0


@pytest.mark.asyncio
async def test_meta_client_test_connection_mock():
    client = MetaClient()
    mock_response = {
        "id": "act_123456789",
        "name": "Acme Brand Official",
        "business_name": "Acme Holdings",
        "currency": "USD",
        "timezone_name": "America/New_York",
        "account_status": 1
    }
    
    with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
        mock_req.return_value = mock_response
        result = await client.test_connection("123456789", "EAABtest_token")
        
        assert result["valid"] is True
        assert result["account_id"] == "act_123456789"
        assert result["account_name"] == "Acme Brand Official"
        assert result["currency"] == "USD"
