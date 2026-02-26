from unittest.mock import patch

import pytest

from database import MonitoredZone
from main import job


@pytest.mark.asyncio
async def test_job_cycle(mock_db_session):
    """Verify the full job cycle: fetch -> calculate -> save."""

    # Mock the monitored zones
    mock_zone = MonitoredZone(geohash="u4p9x", center_lat=60.39, center_lon=5.32)

    # Mock the MET API response
    mock_met_data = {
        "properties": {
            "timeseries": [
                {
                    "time": "2023-10-27T10:00:00Z",
                    "data": {"instant": {"details": {"air_temperature": 10}}},
                }
            ]
        },
        "type": "Feature",
    }

    # Mock the risk calculation result
    mock_risk_result = {"ttf": 5.5, "timestamp": "2023-10-27T10:00:00Z"}

    # We patch AsyncSessionLocal in 'database' so that save_weather_data uses our mock
    # session. We also patch get_monitored_zones to avoid a DB query for zones.
    with (
        patch("database.AsyncSessionLocal", return_value=mock_db_session),
        patch("main.get_monitored_zones", return_value=[mock_zone]),
        patch("met_api.fetch_weather", return_value=mock_met_data),
        patch("risk_calculator.calculate_risk", return_value=mock_risk_result),
    ):
        await job()

        # Verify that data was added to the session
        # We expect 2 additions: 1 for weather data, 1 for risk data
        assert mock_db_session.add.call_count == 2

        # Verify commit was called
        assert mock_db_session.commit.called
