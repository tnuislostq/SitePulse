import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "attribution" in data
        assert "digitalheroesco.com" in data["attribution"]

@pytest.mark.asyncio
async def test_root_attribution():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "digitalheroesco.com" in response.json()["attribution"]

@pytest.mark.asyncio
async def test_ssrf_blocking_localhost():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/audit", json={"url": "http://127.0.0.1:8000"})
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "SecurityValidationError"
