import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """
    Verifies that the API starts and serves the documentation.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
            base_url="http://test",
            follow_redirects=True
    ) as ac:
        response = await ac.get("/api/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_check():
    """
    A simple health check to verify the app is responsive.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True
    ) as ac:
        response = await ac.get("/api/openapi.json")
    assert response.status_code == 200
