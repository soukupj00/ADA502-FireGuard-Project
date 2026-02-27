from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas import SubscriptionRequest, SubscriptionResponse
from app.services.subscription_service import subscribe_to_location_logic

router = APIRouter(prefix="/subscribe", tags=["Subscription"])


@router.post("/", response_model=SubscriptionResponse)
async def subscribe_to_location(
    payload: SubscriptionRequest, db: AsyncSession = Depends(get_db)
) -> SubscriptionResponse:
    """
    Subscribe to a location for fire risk monitoring.

    If the location is not already monitored, it will be added to the monitored zones.
    """
    return await subscribe_to_location_logic(db, payload)
