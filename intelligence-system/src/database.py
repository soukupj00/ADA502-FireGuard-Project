from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    String,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from cities import City
from config import settings

# Database connection
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class FireRiskReading(Base):
    """SQLAlchemy model for fire risk readings."""

    __tablename__ = "fire_risk_readings"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    risk_score = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)


async def create_db_and_tables() -> None:
    """Creates the database and tables if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting an async database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def save_risk_data(city: City, ttf: float) -> None:
    """
    Saves the fire risk data for a given city to the database.

    Args:
        city: The city for which to save the risk data.
        ttf: The time to flashover (in minutes).
    """
    async with AsyncSessionLocal() as db:
        db_reading = FireRiskReading(
            location_name=city["name"],
            latitude=city["lat"],
            longitude=city["lon"],
            risk_score=ttf,
        )
        db.add(db_reading)
        await db.commit()
        await db.refresh(db_reading)
