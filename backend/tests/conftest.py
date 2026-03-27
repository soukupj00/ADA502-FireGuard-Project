from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.auth import (
    get_current_user,
    get_current_user_optional,
    get_current_user_ws_or_sse,
)
from app.db.database import get_db
from app.main import app

# Mock data
MOCK_USER = {"sub": "test-user-id", "preferred_username": "testuser"}
MOCK_GEOHASH = "u4pru"


@pytest.fixture
def mock_risk_reading():
    class Reading:
        def __init__(self):
            self.geohash = MOCK_GEOHASH
            self.latitude = 60.3913
            self.longitude = 5.3221
            self.risk_score = 0.5
            self.risk_category = "Moderate"
            self.ttf = 300.0
            self.prediction_timestamp = datetime.now(timezone.utc)
            self.updated_at = datetime.now(timezone.utc)

    return Reading()


@pytest.fixture
def mock_auth():
    async def override_get_current_user():
        return MOCK_USER

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_user_ws_or_sse] = override_get_current_user
    # Also override the optional auth dependency so endpoints that use it see
    # the mocked authenticated user during tests.
    app.dependency_overrides[get_current_user_optional] = override_get_current_user
    yield
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_current_user_ws_or_sse, None)
    app.dependency_overrides.pop(get_current_user_optional, None)


@pytest.fixture
def mock_db_dep():
    mock_db = AsyncMock()

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    # Yield the same mock_db so tests can assert it was passed to service calls
    yield mock_db
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
