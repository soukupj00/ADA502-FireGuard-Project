from typing import Tuple

import pygeohash as pgh


def get_geohash(lat: float, lon: float, precision: int = 5) -> str:
    """
    Converts latitude and longitude to a geohash string.

    Args:
        lat: Latitude.
        lon: Longitude.
        precision: Length of the geohash string.
                   3 chars ~= 156km x 156km (Coarse Regional Tier)
                   4 chars ~= 39km x 19km (Finer Regional Tier)
                   5 chars ~= 4.9km x 4.9km (Precise Tier for User Alerts)

    Returns:
        The geohash string.
    """
    return pgh.encode(lat, lon, precision=precision)


def get_geohash_center(geohash: str) -> Tuple[float, float]:
    """
    Decodes a geohash string to its center latitude and longitude.

    Args:
        geohash: The geohash string.

    Returns:
        A tuple of (latitude, longitude).
    """
    lat, lon = pgh.decode(geohash)
    # pygeohash returns strings or floats depending on version, ensure float
    return float(lat), float(lon)
