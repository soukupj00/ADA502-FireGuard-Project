from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.models import (
    CurrentFireRisk,
    MonitoredZone,
    WeatherDataReading,
)
from app.services.event_processor_service import (
    process_mqtt_alerts,
    process_thingspeak_analytics,
)


@pytest.fixture
def mock_db_session():
    # Properly mock an AsyncSession and its execute -> scalars -> all/first chain
    session = AsyncMock()
    return session


@pytest.mark.asyncio
@patch("app.services.event_processor_service.mqtt_client")
async def test_process_mqtt_alerts_with_high_risk(mock_mqtt_client, mock_db_session):
    # Mock subscriptions
    mock_sub_result = MagicMock()
    mock_sub_scalars = MagicMock()
    mock_sub_scalars.all.return_value = ["u4pru", "ukmkr"]
    mock_sub_result.scalars.return_value = mock_sub_scalars

    # Mock high risk zones
    mock_risk_result = MagicMock()
    mock_risk_scalars = MagicMock()
    high_risk_zone = CurrentFireRisk(
        geohash="u4pru", risk_category="High", risk_score=75.0
    )
    extreme_risk_zone = CurrentFireRisk(
        geohash="ukmkr", risk_category="Extreme", risk_score=95.0
    )
    mock_risk_scalars.all.return_value = [
        high_risk_zone,
        extreme_risk_zone,
    ]
    mock_risk_result.scalars.return_value = mock_risk_scalars

    # Configure session.execute to return different results based on the query type
    mock_db_session.execute.side_effect = [mock_sub_result, mock_risk_result]

    await process_mqtt_alerts(mock_db_session)

    # Verify mqtt client was called twice
    assert mock_mqtt_client.publish_alert.call_count == 2
    mock_mqtt_client.publish_alert.assert_any_call(
        geohash="u4pru", risk_level="High", risk_score=75.0
    )
    mock_mqtt_client.publish_alert.assert_any_call(
        geohash="ukmkr", risk_level="Extreme", risk_score=95.0
    )


@pytest.mark.asyncio
@patch("app.services.event_processor_service.mqtt_client")
async def test_process_mqtt_alerts_no_subscriptions(mock_mqtt_client, mock_db_session):
    # Mock empty subscriptions
    mock_sub_result = MagicMock()
    mock_sub_scalars = MagicMock()
    mock_sub_scalars.all.return_value = []
    mock_sub_result.scalars.return_value = mock_sub_scalars

    mock_db_session.execute.return_value = mock_sub_result

    await process_mqtt_alerts(mock_db_session)

    # Verify mqtt client was not called
    mock_mqtt_client.publish_alert.assert_not_called()


@pytest.mark.asyncio
@patch("app.services.event_processor_service.thingspeak_client")
async def test_process_thingspeak_analytics(mock_thingspeak, mock_db_session):
    # 1. Mock analytics zones
    mock_zone_result = MagicMock()
    mock_zone_scalars = MagicMock()
    target_zone = MonitoredZone(geohash="u4pru", is_analytics_target=True)
    mock_zone_scalars.all.return_value = [target_zone]
    mock_zone_result.scalars.return_value = mock_zone_scalars

    # 2. Mock current risk
    mock_risk_result = MagicMock()
    mock_risk_scalars = MagicMock()
    current_risk = CurrentFireRisk(geohash="u4pru", risk_score=50.0)
    mock_risk_scalars.first.return_value = current_risk
    mock_risk_result.scalars.return_value = mock_risk_scalars

    # 3. Mock latest weather
    mock_weather_result = MagicMock()
    mock_weather_scalars = MagicMock()
    latest_weather = WeatherDataReading(
        location_name="u4pru",
        data={
            "properties": {
                "timeseries": [
                    {
                        "data": {
                            "instant": {
                                "details": {
                                    "air_temperature": 20.5,
                                    "relative_humidity": 45.0,
                                }
                            }
                        }
                    }
                ]
            }
        },
    )
    mock_weather_scalars.first.return_value = latest_weather
    mock_weather_result.scalars.return_value = mock_weather_scalars

    # Setup the session.execute side effects
    mock_db_session.execute.side_effect = [
        mock_zone_result,
        mock_risk_result,
        mock_weather_result,
    ]

    await process_thingspeak_analytics(mock_db_session)

    # Verify ThingSpeak was called with the correct mapped fields
    mock_thingspeak.push_data.assert_called_once_with(
        {"field1": 20.5, "field2": 45.0, "field3": 50.0}
    )
