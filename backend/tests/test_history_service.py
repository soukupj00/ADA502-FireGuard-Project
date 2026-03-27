from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import FireRiskReading
from app.services.history_service import get_historical_readings_by_geohash


@pytest.fixture
def mock_db_session():
    """Provides a mock SQLAlchemy AsyncSession."""
    session = AsyncMock(spec=AsyncSession)

    # We must explicitly define the entire chain of attributes for the test to work.
    # The return value of session.execute() must have a 'scalars()' method.
    # The return value of that 'scalars()' method must have an 'all()' method.
    # Use MagicMock for the chained return values so `.all()` is a normal method
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = []

    mock_execute_result = MagicMock()
    mock_execute_result.scalars.return_value = mock_scalars

    # session.execute is an async call in production; awaiting it should return
    # our MagicMock execute result (AsyncMock returns its return_value when awaited)
    session.execute.return_value = mock_execute_result

    return session


@pytest.mark.asyncio
async def test_get_history_no_dates(mock_db_session):
    """
    Tests that all readings are returned when no date range is specified.
    """
    geohash = "u4pru"
    now = datetime.now(timezone.utc)
    mock_readings = [
        FireRiskReading(
            location_name=geohash, prediction_timestamp=now - timedelta(days=1)
        ),
        FireRiskReading(
            location_name=geohash, prediction_timestamp=now - timedelta(days=2)
        ),
    ]

    # Correctly configure the mock to return our readings list
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = (
        mock_readings
    )

    result = await get_historical_readings_by_geohash(mock_db_session, geohash)

    assert len(result) == 2
    # The query should be ordered by timestamp descending
    assert result[0].prediction_timestamp > result[1].prediction_timestamp


@pytest.mark.asyncio
async def test_get_history_with_start_date(mock_db_session):
    """
    Tests filtering by a start date.
    """
    geohash = "u4pru"
    start_date = datetime.now(timezone.utc) - timedelta(days=1)

    # This call should be captured by the mock's WHERE clause logic,
    # but for this simple test, we just check the call arguments.
    await get_historical_readings_by_geohash(
        mock_db_session, geohash, start_date=start_date
    )

    # Verify that the select statement was called
    mock_db_session.execute.assert_called_once()
    # Dive into the mock call to check the WHERE clause
    # This is complex, so for now we just ensure it was called.
    # A more advanced test could inspect the SQL expression.


@pytest.mark.asyncio
async def test_get_history_with_end_date(mock_db_session):
    """
    Tests filtering by an end date.
    """
    geohash = "u4pru"
    end_date = datetime.now(timezone.utc)

    await get_historical_readings_by_geohash(
        mock_db_session, geohash, end_date=end_date
    )
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_history_with_date_range(mock_db_session):
    """

    Tests filtering by both a start and end date.
    """
    geohash = "u4pru"
    start_date = datetime.now(timezone.utc) - timedelta(days=5)
    end_date = datetime.now(timezone.utc) - timedelta(days=1)

    await get_historical_readings_by_geohash(
        mock_db_session, geohash, start_date=start_date, end_date=end_date
    )
    mock_db_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_history_no_results(mock_db_session):
    """
    Tests that an empty list is returned when no readings match.
    """
    geohash = "nonexistent"
    result = await get_historical_readings_by_geohash(mock_db_session, geohash)
    assert result == []
    mock_db_session.execute.assert_called_once()
