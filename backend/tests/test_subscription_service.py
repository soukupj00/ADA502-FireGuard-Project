import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import SubscriptionRequest
from app.services.subscription_service import subscribe_to_location_logic


@pytest.fixture
def mock_request():
    request = AsyncMock(spec=Request)
    request.url.path = "/api/v1/users/me/subscriptions/"
    return request


@pytest.mark.asyncio
@patch("app.services.subscription_service.redis_client")
@patch("app.services.subscription_service.get_geohash")
@patch("app.services.subscription_service.get_geohash_center")
async def test_subscribe_to_location_logic_pushes_to_redis(
    mock_center, mock_geohash, mock_redis, mock_request
):
    from unittest.mock import MagicMock

    # Setup
    db = AsyncMock(spec=AsyncSession)
    mock_geohash.return_value = "u4pru"
    mock_center.return_value = (60.39, 5.32)

    # Mock DB result for zone check (not existing)
    mock_zone_result = MagicMock()
    mock_zone_result.scalars.return_value.first.return_value = None
    db.execute.return_value = mock_zone_result

    # Mock for current risk check (not existing)
    # Since it's called twice in the logic (once for zone, once for risk)
    # we might need side_effect or just return the same mock if it works
    db.execute.side_effect = [mock_zone_result, mock_zone_result]

    payload = SubscriptionRequest(latitude=60.39, longitude=5.32)
    user_id = "test-user"

    # Call
    response = await subscribe_to_location_logic(db, payload, user_id, mock_request)

    # Verify
    assert response.geohash == "u4pru"

    # Check if task was pushed to Redis
    mock_redis.lpush.assert_called_once()
    args, _ = mock_redis.lpush.call_args
    assert args[0] == "intelligence_tasks"
    task = json.loads(args[1])
    assert task["action"] == "instant_fetch"
    assert task["geohash"] == "u4pru"
