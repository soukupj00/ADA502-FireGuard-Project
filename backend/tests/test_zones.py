from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from app.db.models import FireRiskReading
from app.schemas import (
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    GeoJSONGeometry,
    GeoJSONProperties,
    Link,
)
from app.utils.constants import RISK_LEGEND_DATA


@pytest.mark.asyncio
@patch("app.routers.zones.get_zones_geojson")
async def test_get_zones(mock_get_zones, client, mock_db_dep):
    """
    Tests the GET /zones/ endpoint for regional zones.
    """
    mock_get_zones.return_value = GeoJSONFeatureCollection(
        features=[
            GeoJSONFeature(
                geometry=GeoJSONGeometry(coordinates=[5.32, 60.39]),
                properties=GeoJSONProperties(geohash="u4pru", is_regional=True),
                _links=[
                    Link(href="/api/v1/risk/u4pru", rel="risk-data"),
                    Link(
                        href="/api/v1/risk/u4pru/history", rel="history"
                    ),  # Now includes history link
                ],
            )
        ],
        risk_legend=RISK_LEGEND_DATA,
        _links=[
            Link(href="/api/v1/zones/", rel="self"),
        ],
    )
    response = await client.get("/api/v1/zones/")
    assert response.status_code == 200
    data = response.json()
    assert "type" in data
    assert data["type"] == "FeatureCollection"
    assert "risk_legend" in data
    assert "_links" in data
    assert "@context" in data
    assert data["@context"]["@vocab"] == "https://purl.org/geojson/vocab#"
    assert any(link["rel"] == "self" for link in data["_links"])
    assert not any(link["rel"] == "subscriptions" for link in data["_links"])

    # Check feature-level links
    feature = data["features"][0]
    assert "_links" in feature
    assert any(link["rel"] == "risk-data" for link in feature["_links"])
    assert any(link["rel"] == "history" for link in feature["_links"])


@pytest.mark.asyncio
@patch("app.routers.zones.get_historical_readings")
async def test_get_zones_history_no_params(mock_get_readings, client, mock_db_dep):
    """
    Tests the GET /zones/history endpoint with no query parameters.
    Should return history for all regional zones.
    """
    geohash = "u4pru"
    now = datetime.now(timezone.utc)
    mock_readings = [
        FireRiskReading(
            geohash=geohash,
            prediction_timestamp=now - timedelta(hours=1),
            risk_score=0.5,
            risk_category="Moderate",
            latitude=60.39,
            longitude=5.32,
        ),
        FireRiskReading(
            geohash=geohash,
            prediction_timestamp=now - timedelta(hours=2),
            risk_score=0.4,
            risk_category="Low",
            latitude=60.39,
            longitude=5.32,
        ),
    ]
    mock_get_readings.return_value = mock_readings

    response = await client.get("/api/v1/zones/history")

    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 2
    assert json_response[0]["properties"]["geohash"] == geohash
    assert any(
        link["rel"] == "history-single-zone" for link in json_response[0]["_links"]
    )
    assert "risk_legend" in json_response[0]
    mock_get_readings.assert_called_once_with(
        db=mock_db_dep, geohashes=None, start_date=None, end_date=None
    )


@pytest.mark.asyncio
@patch("app.routers.zones.get_historical_readings")
async def test_get_zones_history_with_geohashes(mock_get_readings, client, mock_db_dep):
    """
    Tests the GET /zones/history endpoint filtering by a
    comma-separated list of geohashes.
    """
    geohash1 = "u4pru"
    geohash2 = "u4psj"
    now = datetime.now(timezone.utc)
    mock_readings = [
        FireRiskReading(
            geohash=geohash1,
            prediction_timestamp=now - timedelta(hours=1),
            risk_score=0.5,
            risk_category="Moderate",
            latitude=60.39,
            longitude=5.32,
        ),
    ]
    mock_get_readings.return_value = mock_readings
    geohashes_param = f"{geohash1},{geohash2}"

    response = await client.get(f"/api/v1/zones/history?geohashes={geohashes_param}")

    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 1
    assert json_response[0]["properties"]["geohash"] == geohash1
    mock_get_readings.assert_called_once_with(
        db=mock_db_dep, geohashes=[geohash1, geohash2], start_date=None, end_date=None
    )


@pytest.mark.asyncio
@patch("app.routers.zones.get_historical_readings")
async def test_get_zones_history_with_dates(mock_get_readings, client, mock_db_dep):
    """
    Tests the GET /zones/history endpoint filtering by start and end dates.
    """
    geohash = "u4pru"
    now = datetime.now(timezone.utc)
    start_date_str = (now - timedelta(days=2)).isoformat()
    end_date_str = (now - timedelta(days=1)).isoformat()

    mock_readings = [
        FireRiskReading(
            geohash=geohash,
            prediction_timestamp=now - timedelta(days=1, hours=1),
            risk_score=0.5,
            risk_category="Moderate",
            latitude=60.39,
            longitude=5.32,
        ),
    ]
    mock_get_readings.return_value = mock_readings

    response = await client.get(
        f"/api/v1/zones/history?start_date={start_date_str}&end_date={end_date_str}"
    )

    assert response.status_code == 200
    json_response = response.json()
    assert len(json_response) == 1
    assert json_response[0]["properties"]["geohash"] == geohash

    # Verify that datetime objects were passed to the service function
    call_args = mock_get_readings.call_args[1]
    assert isinstance(call_args["start_date"], datetime)
    assert isinstance(call_args["end_date"], datetime)
    assert call_args["start_date"].date() == (now - timedelta(days=2)).date()
    assert call_args["end_date"].date() == (now - timedelta(days=1)).date()


@pytest.mark.asyncio
@patch("app.routers.zones.get_historical_readings")
async def test_get_zones_history_no_results(mock_get_readings, client, mock_db_dep):
    """
    Tests that an empty list is returned when no readings match the criteria.
    """
    mock_get_readings.return_value = []

    response = await client.get("/api/v1/zones/history?geohashes=nonexistent")

    assert response.status_code == 200
    assert response.json() == []
    mock_get_readings.assert_called_once()
