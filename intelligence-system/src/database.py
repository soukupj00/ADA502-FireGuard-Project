from typing import Any, AsyncGenerator, Dict, List, Optional

from models import Base, FireRiskReading, WeatherDataReading  # Import from local models
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import settings

# This part remains specific to the application
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

async def create_db_and_tables() -> None:
    """Creates the database and tables if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting an async database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def save_weather_data(city: Dict[str, Any], weather_json: Dict[str, Any]) -> None:
    """Saves the raw weather data for a given city to the database."""
    async with AsyncSessionLocal() as db:
        db_reading = WeatherDataReading(
            location_name=city["name"],
            latitude=city["lat"],
            longitude=city["lon"],
            data=weather_json,
        )
        db.add(db_reading)
        await db.commit()


async def save_risk_data(city: Dict[str, Any], risk_result: Dict[str, Any]) -> None:
    """Saves the fire risk data for a given city to the database."""
    async with AsyncSessionLocal() as db:
        db_reading = FireRiskReading(
            location_name=city["name"],
            latitude=city["lat"],
            longitude=city["lon"],
            ttf=risk_result["ttf"],
            prediction_timestamp=risk_result["timestamp"],
        )
        db.add(db_reading)
        await db.commit()


async def get_latest_readings(
    location_name: str, limit: int = 1
) -> Dict[str, Optional[List[Any]]]:
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
