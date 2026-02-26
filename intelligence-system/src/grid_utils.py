from typing import List, Tuple

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


def generate_initial_zones() -> List[dict]:
    """
    Generates a list of 'Tier 1' (Regional) zones covering
    the entire bounding box of Norway.
    These zones use coarser geohash precision (3 characters) for a broader overview,
    suitable for a national map.

    Returns:
        A list of dictionaries representing zones.
    """
    zones = []
    seen_hashes = set()

    # Approximate bounding box for Norway
    lat_min, lat_max = 57.9, 71.2
    lon_min, lon_max = 4.6, 31.1

    # Step size in degrees.
    # For precision 3 (approx 156km x 156km), we need larger steps.
    # 1.5 degrees lat is ~166km. 3 degrees lon is ~166km at 60N.
    lat_step = 1.5
    lon_step = 3.0

    current_lat = lat_min
    while current_lat <= lat_max:
        current_lon = lon_min
        while current_lon <= lon_max:
            # Generate a Tier 1 (Regional) geohash (precision 3)
            gh = get_geohash(current_lat, current_lon, precision=3)

            if gh not in seen_hashes:
                lat, lon = get_geohash_center(gh)
                zones.append(
                    {
                        "geohash": gh,
                        "center_lat": lat,
                        "center_lon": lon,
                        "is_regional": True,
                        "name": f"Regional Zone {gh}",
                    }
                )
                seen_hashes.add(gh)

            current_lon += lon_step
        current_lat += lat_step

    return zones
