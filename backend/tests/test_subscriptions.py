from unittest.mock import patch

import pytest
from conftest import MOCK_GEOHASH

from app.schemas import GeoJSONFeatureCollection, SubscriptionResponse
from app.utils.constants import RISK_LEGEND_DATA


@pytest.mark.asyncio
@patch("app.routers.subscription.subscribe_to_location_logic")
async def test_create_subscription_authorized(
    mock_subscribe, client, mock_auth, mock_db_dep
):
    from app.schemas import Link

    mock_subscribe.return_value = SubscriptionResponse(
        geohash=MOCK_GEOHASH,
        status="active",
        message="Subscribed",
        _links=[
            Link(href="/api/v1/users/me/subscriptions/", rel="self"),
            Link(href=f"/api/v1/risk/{MOCK_GEOHASH}", rel="risk-data"),
            Link(
                href=f"/api/v1/users/me/subscriptions/{MOCK_GEOHASH}", rel="unsubscribe"
            ),
            Link(
                href=f"/api/v1/users/me/subscriptions/{MOCK_GEOHASH}/stream",
                rel="stream",
            ),
        ],
    )
    payload = {"geohash": MOCK_GEOHASH}
    response = await client.post(
        "/api/v1/users/me/subscriptions/",
        json=payload,
        headers={"Authorization": "Bearer mock-token"},
    )
    assert response.status_code == 202
    data = response.json()
    assert data["geohash"] == MOCK_GEOHASH
    assert "@context" in data
    assert data["@context"]["@vocab"] == "https://schema.org/"
    assert "_links" in data
    rels = [link["rel"] for link in data["_links"]]
    assert "self" in rels
    assert "risk-data" in rels
    assert "unsubscribe" in rels
    assert "stream" in rels


@pytest.mark.asyncio
async def test_create_subscription_bad_request(client, mock_auth, mock_db_dep):
    # Empty payload, logic should return 400
    payload = {}
    response = await client.post(
        "/api/v1/users/me/subscriptions/",
        json=payload,
        headers={"Authorization": "Bearer mock-token"},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_subscription_unauthorized(client, mock_db_dep):
    payload = {"geohash": MOCK_GEOHASH}
    response = await client.post("/api/v1/users/me/subscriptions/", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
@patch("app.routers.subscription.get_user_subscriptions_logic")
async def test_get_my_subscriptions_authorized(
    mock_get_subs, client, mock_auth, mock_db_dep
):
    from app.schemas import GeoJSONFeature, GeoJSONGeometry, GeoJSONProperties, Link

    mock_get_subs.return_value = GeoJSONFeatureCollection(
        features=[
            GeoJSONFeature(
                geometry=GeoJSONGeometry(coordinates=[5.32, 60.39]),
                properties=GeoJSONProperties(geohash=MOCK_GEOHASH, is_regional=False),
                _links=[
                    Link(href=f"/api/v1/risk/{MOCK_GEOHASH}", rel="risk-data"),
                    Link(
                        href=f"/api/v1/users/me/subscriptions/{MOCK_GEOHASH}",
                        rel="unsubscribe",
                    ),
                    Link(
                        href=f"/api/v1/users/me/subscriptions/{MOCK_GEOHASH}/stream",
                        rel="stream",
                    ),
                ],
            )
        ],
        risk_legend=RISK_LEGEND_DATA,
        _links=[Link(href="/api/v1/users/me/subscriptions/", rel="self")],
    )
    response = await client.get(
        "/api/v1/users/me/subscriptions/",
        headers={"Authorization": "Bearer mock-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "FeatureCollection" in data["type"]
    assert "risk_legend" in data
    assert "@context" in data
    assert data["@context"]["@vocab"] == "https://purl.org/geojson/vocab#"
    assert "_links" in data
    assert any(link["rel"] == "self" for link in data["_links"])

    # Check feature-level links
    feature = data["features"][0]
    assert "_links" in feature
    rels = [link["rel"] for link in feature["_links"]]
    assert "unsubscribe" in rels
    assert "risk-data" in rels
    assert "stream" in rels


@pytest.mark.asyncio
async def test_get_my_subscriptions_unauthorized(client, mock_db_dep):
    response = await client.get("/api/v1/users/me/subscriptions/")
    assert response.status_code == 401


@pytest.mark.asyncio
@patch("app.routers.subscription.unsubscribe_from_location_logic")
async def test_delete_subscription_authorized(
    mock_unsubscribe, client, mock_auth, mock_db_dep
):
    mock_unsubscribe.return_value = None
    response = await client.delete(
        f"/api/v1/users/me/subscriptions/{MOCK_GEOHASH}",
        headers={"Authorization": "Bearer mock-token"},
    )
    assert response.status_code == 204
    mock_unsubscribe.assert_called_once()


@pytest.mark.asyncio
@patch("app.routers.subscription.unsubscribe_from_location_logic")
async def test_delete_subscription_not_found(
    mock_unsubscribe, client, mock_auth, mock_db_dep
):
    from fastapi import HTTPException

    mock_unsubscribe.side_effect = HTTPException(status_code=404, detail="Not found")
    response = await client.delete(
        "/api/v1/users/me/subscriptions/nonexistent",
        headers={"Authorization": "Bearer mock-token"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_subscription_unauthorized(client, mock_db_dep):
    response = await client.delete(f"/api/v1/users/me/subscriptions/{MOCK_GEOHASH}")
    assert response.status_code == 401


@pytest.mark.asyncio
@patch("app.routers.subscription.redis_client")
async def test_stream_subscription_updates_authorized(
    mock_redis, client, mock_auth, mock_db_dep
):
    from unittest.mock import AsyncMock, MagicMock

    # Mock Redis PubSub
    mock_pubsub = MagicMock()
    mock_pubsub.subscribe = AsyncMock()
    mock_pubsub.unsubscribe = AsyncMock()
    mock_redis.pubsub = MagicMock(return_value=mock_pubsub)

    # Mock listen to return one message then stop
    async def mock_listen():
        yield {"type": "message", "data": b"latest-risk-data"}

    mock_pubsub.listen.side_effect = mock_listen

    response = await client.get(
        f"/api/v1/users/me/subscriptions/{MOCK_GEOHASH}/stream",
        headers={"Authorization": "Bearer mock-token"},
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert response.headers["X-Accel-Buffering"] == "no"

    # Read the first chunk
    content = ""
    async for line in response.aiter_lines():
        if line:
            content += line
        if "data: latest-risk-data" in content:
            break

    assert "data: latest-risk-data" in content
