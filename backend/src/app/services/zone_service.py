from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CurrentFireRisk, MonitoredZone
from app.schemas import (
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    GeoJSONGeometry,
    GeoJSONProperties,
)


async def get_zones_geojson(
    db: AsyncSession, regional_only: bool = True
) -> GeoJSONFeatureCollection:
    """
    Get all monitored zones in GeoJSON format.

    This implementation fetches the latest risk data from the CurrentFireRisk table,
    which is updated periodically. This avoids complex queries on the historical
    FireRiskReading table.

    Args:
        regional_only: If True, returns only regional (Tier 1) zones.
                       If False, returns all zones including user-subscribed ones.
    """
    # 1. Fetch zones
    zone_query = select(MonitoredZone)
    if regional_only:
        zone_query = zone_query.where(MonitoredZone.is_regional == True)  # noqa: E712

    zone_result = await db.execute(zone_query)
    zones = zone_result.scalars().all()

    if not zones:
        return GeoJSONFeatureCollection(features=[])

    # 2. Fetch current risks for these zones
    geohashes = [z.geohash for z in zones]
    risk_query = select(CurrentFireRisk).where(CurrentFireRisk.geohash.in_(geohashes))
    risk_result = await db.execute(risk_query)
    risks = risk_result.scalars().all()

    # Map geohash -> risk object
    risk_map = {r.geohash: r for r in risks}

    features = []
    for zone in zones:
        risk_data = risk_map.get(zone.geohash)
        risk_score = risk_data.risk_score if risk_data else None
        risk_category = risk_data.risk_category if risk_data else None

        feature = GeoJSONFeature(
            geometry=GeoJSONGeometry(coordinates=[zone.center_lon, zone.center_lat]),
            properties=GeoJSONProperties(
                geohash=zone.geohash,
                name=zone.name,
                is_regional=zone.is_regional,
                risk_score=risk_score,
                risk_category=risk_category,
                last_updated=zone.last_updated,
            ),
        )
        features.append(feature)

    return GeoJSONFeatureCollection(features=features)
