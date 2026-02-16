# intelligence-system/src/main.py
import asyncio
import logging

from met_api import fetch_weather
from risk_calculator import calculate_risk

# from src.database import save_risk_data  # You need to implement this database insert

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntelligenceSystem")

# List of locations to monitor (Latitude, Longitude)
# Example: Bergen
LOCATIONS = [
    {"name": "Bergen", "lat": 60.3913, "lon": 5.3221},
    # Add more locations here...
]


async def job():
    """The task to run every 10 minutes."""
    logger.info("Starting 10-minute cycle...")

    for loc in LOCATIONS:
        # 1. Fetch Full Series
        met_data = await fetch_weather(loc["lat"], loc["lon"])
        logger.info(
            f"Fetched data for {loc['name']} ({len(met_data['properties']['timeseries'])} timesteps)"
        )

        if met_data:
            # 2. Compute Risk (Using the complex FRCM model)
            risk_result = calculate_risk(met_data)

            if risk_result:
                ttf = risk_result["ttf"]
                logger.info(f"Location: {loc['name']}, TTF: {ttf}")

                # 3. Save to DB
                # await save_risk_data(...)
            else:
                logger.warning(f"Calculation failed for {loc['name']}")
        else:
            logger.warning(f"Skipping {loc['name']} due to fetch error.")


async def main():
    logger.info("Intelligence System Worker Started.")

    while True:
        try:
            await job()

            # Wait for 10 minutes (600 seconds)
            logger.info("Sleeping for 10 minutes...")
            await asyncio.sleep(600)

        except Exception as e:
            logger.error(f"Critical Worker Error: {e}")
            await asyncio.sleep(60)  # Wait 1 min before retrying if crash


if __name__ == "__main__":
    asyncio.run(main())
