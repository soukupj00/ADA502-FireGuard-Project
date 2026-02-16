from fastapi import APIRouter, HTTPException

from app.models import FireRiskRequest, FireRiskResponse

router = APIRouter(prefix="/api/v1/risk", tags=["Fire Risk"])


@router.post("/calculate", response_model=FireRiskResponse)
async def calculate_fire_risk(payload: FireRiskRequest) -> FireRiskResponse:

    # Guard clause example
    if not payload.location_id:
        raise HTTPException(status_code=400, detail="Invalid location ID")

    # Return using RORO pattern with JSON-LD fields
    return FireRiskResponse(
        type="FireRiskEstimate",  # JSON-LD type
        location_id=payload.location_id,
        risk_score=0.85,
        time_to_flashover=5.2,
    )
