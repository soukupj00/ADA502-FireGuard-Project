import logging
from typing import Any, Dict

import httpx

from config import settings

logger = logging.getLogger(__name__)


class ThingSpeakService:
    def __init__(self):
        self.api_key = settings.THINGSPEAK_WRITE_API_KEY
        self.base_url = "https://api.thingspeak.com/update"

    async def push_data(self, data_points: Dict[str, Any]) -> bool:
        """
        Pushes an arbitrary dictionary of data to ThingSpeak fields.
        Keys should be field names (e.g. 'field1', 'field2').
        Values should be the data points.

        Example: data_points = {'field1': 25.5, 'field2': 60, 'field3': 85.0}
        """
        if not self.api_key:
            logger.warning("ThingSpeak API Key not found. Cannot push analytics data.")
            return False

        params = {
            "api_key": self.api_key,
        }

        # Merge the api_key with the data points
        for key, value in data_points.items():
            if value is not None:
                params[key] = str(value)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, params=params)
                response.raise_for_status()  # Raise an exception for bad status codes

                # ThingSpeak returns '0' if the update failed (e.g. rate limit hit)
                # or a channel entry ID if it succeeded.
                if response.text.strip() == "0":
                    logger.error(
                        "ThingSpeak update failed. Rate limit may have been exceeded "
                        "(updates allowed every 15 seconds)."
                    )
                    return False

                logger.info(
                    f"Successfully pushed data to ThingSpeak. Entry ID: {response.text}"
                )
                return True

        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error while pushing to ThingSpeak: {exc}")
        except Exception as exc:
            logger.error(
                f"An unexpected error occurred while pushing to ThingSpeak: {exc}"
            )

        return False


# Singleton instance
thingspeak_client = ThingSpeakService()
