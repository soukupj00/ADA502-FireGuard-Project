# backend/src/app/database.py
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, Float, String

# Cloud-deployable: Use env variable for connection string
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/fireguard_db")

# Async engine setup
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class FireRiskRecord(Base):
    """
    Table for persistent storage of weather data and computed fire risks.
    """
    __tablename__ = "fire_risk_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    location_id: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Weather Inputs (Harvested Data) [cite: 24]
    temperature: Mapped[float] = mapped_column(Float)
    humidity: Mapped[float] = mapped_column(Float)
    wind_speed: Mapped[float] = mapped_column(Float)

    # Computed Outputs
    risk_score: Mapped[float] = mapped_column(Float)
    time_to_flashover: Mapped[float] = mapped_column(Float)


async def get_db():
    """Dependency injection for database sessions."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Creates database tables on application startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)