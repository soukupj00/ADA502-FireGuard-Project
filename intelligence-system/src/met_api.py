import asyncio
import logging
from typing import Any, List

import httpx

from cities import NORWEGIAN_CITIES, City

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MET.no Locationforecast 2.0 Endpoint
MET_URL = "https://api.met.no/weatherapi/locationforecast/2.0/compact"

# MANDATORY: Identify yourself to MET.no
HEADERS = {
    "User-Agent": "FireGuard/1.0 (student.email@uib.no)",
    "Content-Type": "application/json",
}


async def fetch_weather(lat: float, lon: float) -> Any | None:
    """
    Asynchronously fetches weather data for a given latitude and longitude from the
    MET.no API.

    Args:
        lat: The latitude of the location.
        lon: The longitude of the location.

    Returns:
        A dictionary containing the weather data, or None if an error occurs.
    """
    params = {"lat": lat, "lon": lon}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(MET_URL, headers=HEADERS, params=params)
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch MET data: {e}")
            return None


async def fetch_all_weather_data() -> List[Any]:
    """
    Asynchronously fetches weather data for all Norwegian cities.

    Returns:
        A list of dictionaries, where each dictionary contains the weather data for
        a city.
    """
    tasks = [
        fetch_weather(city["lat"], city["lon"]) for city in NORWEGIAN_CITIES
    ]
    weather_data = await asyncio.gather(*tasks)
    return [data for data in weather_data if data is not None]


def get_cities() -> List[City]:
    """
    Returns the list of Norwegian cities.

    Returns:
        A list of dictionaries, where each dictionary represents a city.
    """
    return NORWEGIAN_CITIES
