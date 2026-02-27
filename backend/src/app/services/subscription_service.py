from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CurrentFireRisk, MonitoredZone
from app.schemas import SubscriptionRequest, SubscriptionResponse
from app.utils.grid import get_geohash, get_geohash_center


async def subscribe_to_location_logic(
    db: AsyncSession, payload: SubscriptionRequest
) -> SubscriptionResponse:
    """
    Subscribe to a location for fire risk monitoring.

    If the location is not already monitored, it will be added to the monitored zones.
    """
    # Determine geohash from payload
    if payload.geohash:
        geohash = payload.geohash
    elif payload.latitude is not None and payload.longitude is not None:
        # Calculate geohash with precision 5 (approx 4.9km x 4.9km)
        geohash = get_geohash(payload.latitude, payload.longitude, precision=5)
    else:
        raise HTTPException(
            status_code=400,
            detail="Either geohash or both latitude and longitude must be provided.",
        )

    # Check if the zone already exists
    result = await db.execute(
        select(MonitoredZone).where(MonitoredZone.geohash == geohash)
    )
    existing_zone = result.scalars().first()

    current_risk = None
    if existing_zone:
        # Fetch latest risk reading if available
        risk_result = await db.execute(
            select(CurrentFireRisk).where(CurrentFireRisk.geohash == geohash)
        )
        latest_risk = risk_result.scalars().first()
        if latest_risk:
            current_risk = latest_risk.ttf

        return SubscriptionResponse(
            geohash=geohash,
            status="active",
            message="Location is already being monitored.",
            current_risk=current_risk,
        )

    # If not, create a new zone
    center_lat, center_lon = get_geohash_center(geohash)

    new_zone = MonitoredZone(
        geohash=geohash,
        center_lat=center_lat,
        center_lon=center_lon,
        is_regional=False,  # User subscription, not a regional zone
        name=f"User Subscription {geohash}",
    )

    db.add(new_zone)
    await db.commit()

    return SubscriptionResponse(
        geohash=geohash,
        status="pending",
        message="Location added to monitoring queue. Data will be available shortly.",
        current_risk=None,
    )
