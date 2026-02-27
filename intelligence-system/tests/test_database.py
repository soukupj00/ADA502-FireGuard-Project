from unittest.mock import patch

import pytest

from db.database import (
    MonitoredZone,
    get_monitored_zones,
    save_risk_data,
    save_weather_data,
)


@pytest.mark.asyncio
async def test_save_weather_data(mock_db_session):
    """Verify that weather data is saved correctly."""

    # Mock the AsyncSessionLocal to return our mock session
    with patch("db.database.AsyncSessionLocal", return_value=mock_db_session):
        await save_weather_data(
            location_name="u4p9x", lat=60.39, lon=5.32, weather_json={"temp": 10}
        )

        # Verify that add() was called with a WeatherDataReading object
        assert mock_db_session.add.called
        args, _ = mock_db_session.add.call_args
        reading = args[0]

        assert reading.location_name == "u4p9x"
        assert reading.latitude == 60.39
        assert reading.longitude == 5.32
        assert reading.data == {"temp": 10}

        # Verify commit() was called
        assert mock_db_session.commit.called


@pytest.mark.asyncio
async def test_save_risk_data(mock_db_session):
    """Verify that risk data is saved correctly."""

    with patch("db.database.AsyncSessionLocal", return_value=mock_db_session):
        await save_risk_data(
            location_name="u4p9x",
            lat=60.39,
            lon=5.32,
            risk_result={"ttf": 5.5, "timestamp": "2023-10-27T10:00:00Z"},
        )

        assert mock_db_session.add.called
        args, _ = mock_db_session.add.call_args
        reading = args[0]

        assert reading.location_name == "u4p9x"
        assert reading.ttf == 5.5
        assert reading.prediction_timestamp == "2023-10-27T10:00:00Z"

        assert mock_db_session.commit.called


@pytest.mark.asyncio
async def test_get_monitored_zones(mock_db_session):
    """Verify that we can retrieve monitored zones."""

    # Mock the result of the query
    mock_zone = MonitoredZone(geohash="u4p9x", center_lat=60.39, center_lon=5.32)
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = [
        mock_zone
    ]

    with patch("db.database.AsyncSessionLocal", return_value=mock_db_session):
        zones = await get_monitored_zones()

        assert len(zones) == 1
        assert zones[0].geohash == "u4p9x"
        assert zones[0].center_lat == 60.39
