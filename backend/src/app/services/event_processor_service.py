import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import AsyncSessionLocal
from app.db.models import (
    CurrentFireRisk,
    MonitoredZone,
    UserSubscription,
    WeatherDataReading,
)
from app.services.mqtt_service import mqtt_client
from app.services.thingspeak_service import thingspeak_client

logger = logging.getLogger(__name__)


async def process_hourly_data_ready_event():
    """
    Main orchestration function triggered by the HOURLY_DATA_READY Redis event.
    """
    logger.info("Processing HOURLY_DATA_READY event...")

    async with AsyncSessionLocal() as db:
        await process_mqtt_alerts(db)
        await process_thingspeak_analytics(db)

    logger.info("Finished processing HOURLY_DATA_READY event.")


async def process_mqtt_alerts(db: AsyncSession):
    """
    Finds geohashes with active user subscriptions that are in High or Extreme risk,
    and publishes MQTT alerts for them.
    """
    try:
        # 1. Get all unique geohashes that users are subscribed to
        sub_query = select(UserSubscription.geohash).distinct()
        sub_result = await db.execute(sub_query)
        subscribed_geohashes = sub_result.scalars().all()

        if not subscribed_geohashes:
            logger.info("No active user subscriptions found. Skipping MQTT alerts.")
            return

        # 2. Find which of these subscribed geohashes are in High/Extreme risk
        risk_query = select(CurrentFireRisk).where(
            CurrentFireRisk.geohash.in_(subscribed_geohashes),
            CurrentFireRisk.risk_category.in_(["High", "Extreme"]),
        )
        risk_result = await db.execute(risk_query)
        high_risk_zones = risk_result.scalars().all()

        if not high_risk_zones:
            logger.info("No subscribed zones are currently at High/Extreme risk.")
            return

        # 3. Publish alerts
        for risk in high_risk_zones:
            mqtt_client.publish_alert(
                geohash=risk.geohash,
                risk_level=risk.risk_category,
                risk_score=risk.risk_score,
            )

    except Exception as e:
        logger.error(f"Error processing MQTT alerts: {e}")


async def process_thingspeak_analytics(db: AsyncSession):
    """
    Finds zones marked as analytics targets and pushes their latest data to ThingSpeak.
    """
    try:
        # 1. Get zones marked for analytics
        zone_query = select(MonitoredZone).where(MonitoredZone.is_analytics_target)
        zone_result = await db.execute(zone_query)
        analytics_zones = zone_result.scalars().all()

        if not analytics_zones:
            logger.info(
                "No zones marked as analytics targets. Skipping ThingSpeak push."
            )
            return

        # For simplicity in this example, we assume we push fields for up to 2 zones
        # mapping them to specific ThingSpeak fields.
        # E.g., Zone 1 -> field1 (temp), field2 (hum), field3 (risk)
        #       Zone 2 -> field4 (temp), field5 (hum), field6 (risk)

        data_points = {}
        field_index = 1

        for zone in analytics_zones:
            # We need the latest risk and weather for this zone
            risk_query = select(CurrentFireRisk).where(
                CurrentFireRisk.geohash == zone.geohash
            )
            risk_result = await db.execute(risk_query)
            current_risk = risk_result.scalars().first()

            weather_query = (
                select(WeatherDataReading)
                .where(WeatherDataReading.location_name == zone.geohash)
                .order_by(WeatherDataReading.recorded_at.desc())
                .limit(1)
            )
            weather_result = await db.execute(weather_query)
            latest_weather = weather_result.scalars().first()

            if current_risk and latest_weather:
                # Extract temperature and humidity
                # The IS stores the raw MET JSON feature in `data`
                try:
                    timeseries = latest_weather.data.get("properties", {}).get(
                        "timeseries", []
                    )
                    if timeseries:
                        details = (
                            timeseries[0]
                            .get("data", {})
                            .get("instant", {})
                            .get("details", {})
                        )
                        temp = details.get("air_temperature")
                        hum = details.get("relative_humidity")

                        data_points[f"field{field_index}"] = temp
                        data_points[f"field{field_index + 1}"] = hum
                        data_points[f"field{field_index + 2}"] = current_risk.risk_score

                        field_index += 3
                except Exception as parse_error:
                    logger.error(
                        f"Error parsing weather data for ThingSpeak: {parse_error}"
                    )

            # ThingSpeak only supports up to 8 fields per channel
            if field_index > 6:
                break

        if data_points:
            await thingspeak_client.push_data(data_points)
        else:
            logger.warning("No complete data found to push to ThingSpeak.")

    except Exception as e:
        logger.error(f"Error processing ThingSpeak analytics: {e}")
