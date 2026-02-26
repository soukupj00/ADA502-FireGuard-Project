from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def mock_db_session():
    """
    Creates a mock AsyncSession for testing database interactions without a real DB.
    """
    session = AsyncMock(spec=AsyncSession)
    # Mock the execute method to return a mock result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalars.return_value.first.return_value = None
    session.execute.return_value = mock_result
    return session
