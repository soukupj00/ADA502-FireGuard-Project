from unittest.mock import patch

import pytest

from database import MonitoredZone
from main import job


@pytest.mark.asyncio
async def test_job_cycle(mock_db_session):
    """Verify the full job cycle: fetch -> calculate -> save."""

    # Mock the monitored zones
    mock_zone = MonitoredZone(geohash="u4p9x", center_lat=60.39, center_lon=5.32)
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = [
        mock_zone
    ]

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

    with (
        patch("database.AsyncSessionLocal", return_value=mock_db_session),
        patch("met_api.fetch_weather", return_value=mock_met_data),
        patch("risk_calculator.calculate_risk", return_value=mock_risk_result),
        patch("database.save_weather_data") as mock_save_weather,
        patch("database.save_risk_data") as mock_save_risk,
    ):
        await job()

        # Verify that we fetched weather for the zone
        assert mock_save_weather.called
        args, _ = mock_save_weather.call_args
        assert args[0] == "u4p9x"
        assert args[1] == 60.39
        assert args[2] == 5.32
        assert args[3] == mock_met_data

        # Verify that we calculated risk
        assert mock_save_risk.called
        args, _ = mock_save_risk.call_args
        assert args[0] == "u4p9x"
        assert args[1] == 60.39
        assert args[2] == 5.32
        assert args[3] == mock_risk_result
