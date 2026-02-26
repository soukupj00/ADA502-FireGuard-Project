from pydantic import BaseModel, Field
from datetime import datetime

class FireRiskRequest(BaseModel):
    """Request model for fire risk prediction."""
    temperature: float = Field(..., example=25.5, description="Temperature in Celsius")
    humidity: float = Field(..., example=60.0, description="Relative humidity in percent")
    wind_speed: float = Field(..., example=10.0, description="Wind speed in km/h")

class FireRiskResponse(BaseModel):
    """Response model for fire risk prediction."""
    risk_score: float = Field(..., example=0.75, description="Calculated fire risk score (0 to 1)")
    time_to_flashover: float = Field(..., example=300.5, description="Estimated time to flashover in seconds")
    recommendation: str = Field(..., example="High risk: consider evacuation.", description="Plain-text safety recommendation")
    timestamp: datetime = Field(..., description="Timestamp of the prediction")
