# intelligence-system/src/main.py
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from database import (
    create_db_and_tables,
    get_latest_readings,
    save_risk_data,
    save_weather_data,
)
from met_api import fetch_all_weather_data, get_cities
from risk_calculator import calculate_risk

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntelligenceSystem")


def save_to_json(data: Any, filename: str) -> None:
    """
    Saves the given data to a JSON file.

    Args:
        data: The data to save.
        filename: The name of the file to save the data to.
    """
    with open(filename, "w") as f:
        json.dump(data, f, indent=4, default=str)


async def job() -> None:
    """
    Fetches weather data, calculates fire risk, and saves it to the database.
    """
    logger.info("Starting 10-minute cycle...")

    cities = get_cities()
    weather_data_list = await fetch_all_weather_data()

    # Save weather data to a file
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    weather_data_filename = f"output/weather_data_{timestamp}.json"
    save_to_json(weather_data_list, weather_data_filename)
    logger.info(f"Saved weather data to {weather_data_filename}")

    risk_results = []
    for i, met_data in enumerate(weather_data_list):
        city = cities[i]
        timesteps = len(met_data["properties"]["timeseries"])
        logger.info(f"Fetched data for {city['name']} ({timesteps} timesteps)")

        # Save raw weather data to the database
        await save_weather_data(city, met_data)

        if met_data:
            # 2. Compute Risk (Using the complex FRCM model)
            risk_result = calculate_risk(met_data)

            if risk_result:
                logger.info(
                    f"Location: {city['name']}, TTF: {risk_result['ttf']}"
                )
                risk_results.append(
                    {
                        "city": city["name"],
                        "ttf": risk_result["ttf"],
                        "timestamp": risk_result["timestamp"],
                    }
                )

                # 3. Save to DB
                await save_risk_data(city, risk_result)
            else:
                logger.warning(f"Calculation failed for {city['name']}")
        else:
            logger.warning(f"Skipping {city['name']} due to fetch error.")

    # Save risk results to a file
    risk_results_filename = f"output/risk_results_{timestamp}.json"
    save_to_json(risk_results, risk_results_filename)
    logger.info(f"Saved risk results to {risk_results_filename}")

    # --- Debug Function Call ---
    # Fetch and print the latest reading for sample cities
    latest_oslo_data = await get_latest_readings("Oslo")
    logger.info(f"DEBUG - Latest Oslo Data: {latest_oslo_data}")
    latest_bergen_data = await get_latest_readings("Bergen")
    logger.info(f"DEBUG - Latest Bergen Data: {latest_bergen_data}")


async def main() -> None:
    """
    The main function that runs the intelligence system worker.
    """
    logger.info("Intelligence System Worker Started.")
    # Create output directory if it doesn't exist
    Path("output").mkdir(exist_ok=True)
    await create_db_and_tables()

    while True:
        try:
            await job()

            # Wait for 10 minutes (600 seconds)
            logger.info("Sleeping for 10 minutes...")
            await asyncio.sleep(600)

        except Exception as e:
            logger.error(f"Critical Worker Error: {e}", exc_info=True)
            await asyncio.sleep(60)  # Wait 1 min before retrying if crash


if __name__ == "__main__":
    asyncio.run(main())
