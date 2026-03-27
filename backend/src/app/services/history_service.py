from datetime import datetime, time
from typing import List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import FireRiskReading, MonitoredZone


async def get_historical_readings(
    db: AsyncSession,
    geohashes: Optional[List[str]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> Sequence[FireRiskReading]:
    """
    Retrieves historical fire risk readings from the database, with flexible filtering.

    Args:
        db: The database session.
        geohashes: An optional list of geohashes to filter by. If None, it will
                   default to all regional zones.
        start_date: The start of the date range.
        end_date: The end of the date range.

    Returns:
        A sequence of historical fire risk readings.
    """
    # Base statement
    stmt = select(FireRiskReading).order_by(FireRiskReading.prediction_timestamp.desc())

    # If no specific geohashes are provided, default to all regional zones.
    if geohashes is None:
        regional_geohashes_query = select(MonitoredZone.geohash).where(
            MonitoredZone.is_regional
        )
        regional_geohashes_result = await db.execute(regional_geohashes_query)
        geohashes_to_filter = regional_geohashes_result.scalars().all()
        stmt = stmt.where(FireRiskReading.geohash.in_(geohashes_to_filter))
    else:
        stmt = stmt.where(FireRiskReading.geohash.in_(geohashes))

    # Apply date filtering
    if start_date:
        start_datetime = datetime.combine(start_date.date(), time.min)
        stmt = stmt.where(FireRiskReading.prediction_timestamp >= start_datetime)

    if end_date:
        end_datetime = datetime.combine(end_date.date(), time.max)
        stmt = stmt.where(FireRiskReading.prediction_timestamp <= end_datetime)

    result = await db.execute(stmt)
    return result.scalars().all()
