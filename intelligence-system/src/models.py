from datetime import datetime, timezone  # Import timezone
from typing import Any

from sqlalchemy import JSON, DateTime, Float, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models, providing a common metadata store."""

    pass


class WeatherDataReading(Base):
    """
    Represents a single reading of raw weather data from an external API,
    stored in a JSON format for flexibility and future analysis.
    """

    __tablename__ = "weather_data_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_name: Mapped[str] = mapped_column(String, index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),  # Tell SQLAlchemy to expect timezone-aware datetimes
        default=lambda: datetime.now(timezone.utc),  # Use a timezone-aware default
        index=True,
    )
    data: Mapped[dict[str, Any]] = mapped_column(JSON)

    def __repr__(self) -> str:
        return (f"<WeatherDataReading(id={self.id}, location='{self.location_name}', "
                f"recorded_at='{self.recorded_at}')>")


class FireRiskReading(Base):
    """
    Represents the calculated fire risk for a specific location at a given time,
    based on weather data and the fire risk calculation model.
    """

    __tablename__ = "fire_risk_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_name: Mapped[str] = mapped_column(String, index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),  # Tell SQLAlchemy to expect timezone-aware datetimes
        default=lambda: datetime.now(timezone.utc),  # Use a timezone-aware default
        index=True,
    )
    prediction_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ttf: Mapped[float] = mapped_column(Float)

    def __repr__(self) -> str:
        return (f"<FireRiskReading(id={self.id}, location='{self.location_name}', "
                f"ttf={self.ttf})>")
