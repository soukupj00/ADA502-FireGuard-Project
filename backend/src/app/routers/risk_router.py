from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import CurrentFireRisk
from app.schemas import FireRiskReadingSchema
from app.services.risk_service import (
    get_latest_risk_by_coords,
    get_latest_risk_reading,
)

router = APIRouter(prefix="/api/v1/risk", tags=["Fire Risk"])


@router.get("/{geohash}", response_model=FireRiskReadingSchema)
async def get_risk_by_geohash(
    geohash: str, db: AsyncSession = Depends(get_db)
) -> CurrentFireRisk:
    """
    Get the latest fire risk reading for a specific geohash.
    """
    reading = await get_latest_risk_reading(db, geohash)

    if not reading:
        raise HTTPException(
            status_code=404, detail="Risk data not found for this location"
        )

    return reading


@router.get("/coords", response_model=FireRiskReadingSchema)
async def get_risk_by_coords(
    latitude: float, longitude: float, db: AsyncSession = Depends(get_db)
) -> CurrentFireRisk:
    """
    Get the latest fire risk reading for a location by coordinates.
    """
    reading = await get_latest_risk_by_coords(db, latitude, longitude)

    if not reading:
        raise HTTPException(
            status_code=404, detail="Risk data not found for this location"
        )

    return reading
