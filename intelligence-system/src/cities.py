
from typing import List, TypedDict


class City(TypedDict):
    """A dictionary representing a city with its name, latitude, and longitude."""

    name: str
    lat: float
    lon: float


NORWEGIAN_CITIES: List[City] = [
    {"name": "Oslo", "lat": 59.9139, "lon": 10.7522},
    {"name": "Bergen", "lat": 60.3913, "lon": 5.3221},
    {"name": "Trondheim", "lat": 63.4305, "lon": 10.3951},
    {"name": "Stavanger", "lat": 58.9700, "lon": 5.7331},
    {"name": "Drammen", "lat": 59.7439, "lon": 10.2045},
    {"name": "Fredrikstad", "lat": 59.2170, "lon": 10.9340},
    {"name": "Porsgrunn", "lat": 59.1405, "lon": 9.6561},
    {"name": "Skien", "lat": 59.2096, "lon": 9.6088},
    {"name": "Kristiansand", "lat": 58.1468, "lon": 7.9952},
    {"name": "Ålesund", "lat": 62.4722, "lon": 6.1495},
    {"name": "Tønsberg", "lat": 59.2678, "lon": 10.4076},
    {"name": "Moss", "lat": 59.4346, "lon": 10.6584},
    {"name": "Sarpsborg", "lat": 59.2858, "lon": 11.1120},
    {"name": "Bodø", "lat": 67.2800, "lon": 14.4050},
    {"name": "Arendal", "lat": 58.4600, "lon": 8.7694},
    {"name": "Haugesund", "lat": 59.4139, "lon": 5.2682},
    {"name": "Sandefjord", "lat": 59.1333, "lon": 10.2167},
    {"name": "Tromsø", "lat": 69.6492, "lon": 18.9553},
    {"name": "Hamar", "lat": 60.7945, "lon": 11.0679},
    {"name": "Gjøvik", "lat": 60.7954, "lon": 10.6917},
    {"name": "Larvik", "lat": 59.0533, "lon": 10.0352},
    {"name": "Askøy", "lat": 60.4000, "lon": 5.2167},
    {"name": "Lillestrøm", "lat": 59.9579, "lon": 11.0499},
    {"name": "Molde", "lat": 62.7374, "lon": 7.1591},
    {"name": "Harstad", "lat": 68.7998, "lon": 16.5435},
    {"name": "Kristiansund", "lat": 63.1111, "lon": 7.7325},
    {"name": "Lillehammer", "lat": 61.1153, "lon": 10.4663},
    {"name": "Horten", "lat": 59.4167, "lon": 10.4833},
    {"name": "Kongsberg", "lat": 59.6678, "lon": 9.6472},
    {"name": "Halden", "lat": 59.1250, "lon": 11.3833},
]
