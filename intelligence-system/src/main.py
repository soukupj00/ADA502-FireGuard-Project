# intelligence-system/src/main.py
import asyncio
import logging

from config import settings
from db.database import (
    create_db_and_tables,
    get_latest_readings,
    get_monitored_zones,
    save_risk_data,
    save_weather_data,
    seed_initial_zones,
)
from utils.met_api import fetch_weather
from utils.risk_calculator import calculate_risk

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntelligenceSystem")


async def job() -> None:
    """
    Fetches weather data for all monitored zones, calculates fire risk,
    and saves the results to the database.
    """
    logger.info("Starting fetch cycle...")

    monitored_zones = await get_monitored_zones()
    logger.info(f"Found {len(monitored_zones)} zones to monitor.")

    for zone in monitored_zones:
        logger.info(f"Processing zone: {zone.name} ({zone.geohash})")

        # 1. Fetch weather for the center of the zone
        met_data = await fetch_weather(zone.center_lat, zone.center_lon)

        if not met_data:
            logger.warning(f"Skipping zone {zone.geohash} due to fetch error.")
            continue

        # Save raw weather data to the database
        await save_weather_data(
            location_name=zone.geohash,
            lat=zone.center_lat,
            lon=zone.center_lon,
            weather_json=met_data,
        )

        # 2. Compute Risk
        risk_result = calculate_risk(met_data)

        if risk_result:
            logger.info(f"Zone: {zone.geohash}, TTF: {risk_result['ttf']}")

            # 3. Save risk result to DB
            await save_risk_data(
                location_name=zone.geohash,
                lat=zone.center_lat,
                lon=zone.center_lon,
                risk_result=risk_result,
            )
        else:
            logger.warning(f"Risk calculation failed for zone {zone.geohash}")

    # --- Debug Function Call ---
    # Fetch and print the latest reading for a sample zone
    if monitored_zones:
        sample_geohash = monitored_zones[0].geohash
        latest_data = await get_latest_readings(sample_geohash)
        logger.info(f"DEBUG - Latest data for {sample_geohash}: {latest_data}")


async def main() -> None:
    """
    The main function that runs the intelligence system worker.
    """
    logger.info("Intelligence System Worker Started.")

    # Create DB tables and seed with initial zones
    await create_db_and_tables()
    await seed_initial_zones()

    while True:
        try:
            await job()
            logger.info(
                "Sleeping for %s seconds...",
                settings.FETCH_INTERVAL_SECONDS,
            )
            await asyncio.sleep(settings.FETCH_INTERVAL_SECONDS)
        except Exception as e:
            logger.error(f"Critical Worker Error: {e}", exc_info=True)
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
