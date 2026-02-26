from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_db_session():
    """
    Creates a mock database session for testing.
    We construct this manually to ensure strict control over sync vs async methods.
    """
    session = MagicMock()

    # Make it an async context manager
    # async with session: -> returns session
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)

    # Async methods
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()

    # Sync methods
    session.add = MagicMock()

    # Configure the result object returned by execute
    # execute() -> await -> Result
    mock_result = MagicMock()
    session.execute.return_value = mock_result

    # Result.scalars() -> ScalarResult
    mock_scalars = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    # ScalarResult.all() -> list
    mock_scalars.all.return_value = []
    mock_scalars.first.return_value = None

    return session
