import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)
from backend.config import settings


def test_password_hashing_and_verification():
    raw_pwd = "MySuperSecretPassword123!"
    pwd_hash = hash_password(raw_pwd)
    
    assert pwd_hash.startswith("pbkdf2_sha256$100000$")
    assert verify_password(raw_pwd, pwd_hash) is True
    assert verify_password("WrongPassword", pwd_hash) is False
    assert verify_password(raw_pwd, "invalid_hash_string") is False


def test_jwt_token_lifecycle():
    user_data = {"sub": "rajsolanki32@gmail.com", "role": "admin"}
    token = create_access_token(user_data)
    assert isinstance(token, str)
    
    decoded = decode_access_token(token)
    assert decoded["sub"] == "rajsolanki32@gmail.com"
    assert decoded["role"] == "admin"
    assert decoded["iss"] == "creative-leaderboard-auth"


@pytest.mark.asyncio
async def test_auth_login_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/auth/login", json={
            "email": "rajsolanki32@gmail.com",
            "password": "R44414441r@"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["sub"] == "rajsolanki32@gmail.com"


@pytest.mark.asyncio
async def test_auth_login_invalid_credentials():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Wrong password
        res1 = await ac.post("/api/auth/login", json={
            "email": "rajsolanki32@gmail.com",
            "password": "WrongPassword123"
        })
        assert res1.status_code == 401

        # Wrong email
        res2 = await ac.post("/api/auth/login", json={
            "email": "intruder@example.com",
            "password": "R44414441r@"
        })
        assert res2.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoints_require_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Accessing protected endpoint without token should return 401
        res_unauthorized = await ac.get("/api/leaderboard")
        assert res_unauthorized.status_code == 401

        # 2. Login to get valid token
        login_res = await ac.post("/api/auth/login", json={
            "email": "rajsolanki32@gmail.com",
            "password": "R44414441r@"
        })
        token = login_res.json()["access_token"]

        # 3. Access with Bearer token should succeed
        headers = {"Authorization": f"Bearer {token}"}
        res_authorized = await ac.get("/api/leaderboard", headers=headers)
        assert res_authorized.status_code == 200

        # 4. /api/health remains public
        res_health = await ac.get("/api/health")
        assert res_health.status_code == 200
