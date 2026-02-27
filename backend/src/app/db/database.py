from typing import Any, AsyncGenerator, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.models import Base, MonitoredZone
from config import settings

# Database connection
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


async def create_db_and_tables() -> None:
    """Creates the database and tables if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_monitored_zones() -> Sequence[Any]:
    """Returns all active monitored zones."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(MonitoredZone))
        return result.scalars().all()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting an async database session."""
    async with AsyncSessionLocal() as session:
        yield session
