# backend/src/app/models.py

from pydantic import BaseModel, ConfigDict, Field


class JsonLdBase(BaseModel):
    """Base model for JSON-LD responses using aliasing."""

    context: str = Field(default="https://schema.org", alias="@context")
    type: str = Field(alias="@type")

    model_config = ConfigDict(populate_by_name=True)


class FireRiskRequest(BaseModel):
    location_id: str
    # Add other fields required for calculation


class FireRiskResponse(JsonLdBase):
    location_id: str
    risk_score: float
    time_to_flashover: float
