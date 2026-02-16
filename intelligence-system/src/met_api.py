import logging

import httpx

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


async def fetch_weather(lat: float, lon: float):
    params = {"lat": lat, "lon": lon}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(MET_URL, headers=HEADERS, params=params)
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch MET data: {e}")
            return None
