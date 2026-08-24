import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.services.auth_service import create_access_token


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "timestamp" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["health"] == "/api/health"
        assert data["docs"] == "/docs"


@pytest.mark.asyncio
async def test_import_preview_endpoint():
    transport = ASGITransport(app=app)
    token = create_access_token({"sub": "rajsolanki32@gmail.com", "role": "admin"})
    headers = {"Authorization": f"Bearer {token}"}
    
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "client_id": "mock_client_1",
            "raw_text": "Ad Name,Spend,Purchase ROAS,Purchases\nCreative Hero,$400.00,3.2,12"
        }
        response = await ac.post("/api/import/preview", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["total_rows"] == 1
        assert data["rows"][0]["name"] == "Creative Hero"
        assert data["rows"][0]["spend"] == 400.0
        assert data["rows"][0]["roas"] == 3.2
