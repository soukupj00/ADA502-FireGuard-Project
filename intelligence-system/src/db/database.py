from typing import Any, AsyncGenerator, Dict, Sequence

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    func,
    select,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import settings
from utils.grid_utils import generate_initial_zones

# Database connection
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class MonitoredZone(Base):
    """
    Represents a geographic zone (grid cell) that we are actively monitoring.
    """

    __tablename__ = "monitored_zones"

    geohash = Column(String, primary_key=True, index=True)
    center_lat = Column(Float, nullable=False)
    center_lon = Column(Float, nullable=False)
    is_regional = Column(
        Boolean, default=True
    )  # True = Tier 1 (Map), False = Tier 2 (User)
    name = Column(String, nullable=True)  # Optional descriptive name
    last_updated = Column(DateTime(timezone=True), server_default=func.now())


class WeatherDataReading(Base):
    """SQLAlchemy model for raw weather data readings."""

    __tablename__ = "weather_data_readings"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, index=True)  # Can be geohash or city name
    latitude = Column(Float)
    longitude = Column(Float)
    data = Column(JSONB)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class FireRiskReading(Base):
    """SQLAlchemy model for fire risk readings."""

    __tablename__ = "fire_risk_readings"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, index=True)  # Can be geohash or city name
    latitude = Column(Float)
    longitude = Column(Float)
    ttf = Column(Float)
    prediction_timestamp = Column(DateTime(timezone=True))
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


async def create_db_and_tables() -> None:
    """Creates the database and tables if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_initial_zones() -> None:
    """
    Populates the database with initial regional zones if empty.
    """
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(MonitoredZone).limit(1))
        if result.first() is None:
            initial_zones = generate_initial_zones()
            for zone_data in initial_zones:
                zone = MonitoredZone(**zone_data)
                db.add(zone)
            await db.commit()


async def get_monitored_zones() -> Sequence[Any]:
    """Returns all active monitored zones."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(MonitoredZone))
        return result.scalars().all()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting an async database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def save_weather_data(
    location_name: str, lat: float, lon: float, weather_json: Dict[str, Any]
) -> None:
    """Saves the raw weather data for a given location to the database."""
    async with AsyncSessionLocal() as db:
        db_reading = WeatherDataReading(
            location_name=location_name,
            latitude=lat,
            longitude=lon,
            data=weather_json,
        )
        db.add(db_reading)
        await db.commit()


async def save_risk_data(
    location_name: str, lat: float, lon: float, risk_result: Dict[str, Any]
) -> None:
    """Saves the fire risk data for a given location to the database."""
    async with AsyncSessionLocal() as db:
        db_reading = FireRiskReading(
            location_name=location_name,
            latitude=lat,
            longitude=lon,
            ttf=risk_result["ttf"],
            prediction_timestamp=risk_result["timestamp"],
        )
        db.add(db_reading)
        await db.commit()


async def get_latest_readings(
    location_name: str, limit: int = 1
) -> dict[str, Sequence[Any]]:
    """
    Debug function to get the latest weather and fire risk readings for a location.
    """
    async with AsyncSessionLocal() as db:
        weather_result = await db.execute(
            select(WeatherDataReading)
            .where(WeatherDataReading.location_name == location_name)
            .order_by(WeatherDataReading.recorded_at.desc())
            .limit(limit)
        )
        weather_readings = weather_result.scalars().all()

        risk_result = await db.execute(
            select(FireRiskReading)
            .where(FireRiskReading.location_name == location_name)
            .order_by(FireRiskReading.recorded_at.desc())
            .limit(limit)
        )
        risk_readings = risk_result.scalars().all()

        return {
            "weather_data": weather_readings,
            "fire_risk_data": risk_readings,
        }
