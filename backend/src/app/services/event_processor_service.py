import logging

import pygeohash as pgh
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import AsyncSessionLocal
from app.db.models import (
    CurrentFireRisk,
    UserSubscription,
)
from app.services.mqtt_service import mqtt_client
from app.services.thingspeak_service import thingspeak_client
from app.utils.constants import ANALYTICS_CITIES

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
    Pushes fire risk data for 7 major Norwegian cities and a national average
    to a ThingSpeak channel.
    """
    try:
        city_geohashes = {
            city["name"]: pgh.encode(city["latitude"], city["longitude"], precision=5)
            for city in ANALYTICS_CITIES
        }

        # Fetch risk scores for the target cities
        risk_query = select(CurrentFireRisk).where(
            CurrentFireRisk.geohash.in_(city_geohashes.values())
        )
        risk_result = await db.execute(risk_query)
        city_risks = {risk.geohash: risk.risk_score for risk in risk_result.scalars()}

        # Calculate national average risk score
        avg_query = select(func.avg(CurrentFireRisk.risk_score))
        avg_result = await db.execute(avg_query)
        national_average = avg_result.scalar_one_or_none()

        # Prepare data points for ThingSpeak
        data_points = {}
        for i, city in enumerate(ANALYTICS_CITIES, 1):
            geohash = city_geohashes[city["name"]]
            data_points[f"field{i}"] = city_risks.get(geohash)

        if national_average is not None:
            data_points["field8"] = national_average

        if data_points:
            await thingspeak_client.push_data(data_points)
        else:
            logger.warning("No data found to push to ThingSpeak.")

    except Exception as e:
        logger.error(f"Error processing ThingSpeak analytics: {e}")
