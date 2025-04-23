import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.core.database import init_db

@pytest.mark.asyncio
@patch("app.core.database.engine")
async def test_init_db_success(mock_engine):
    # Mock the `begin` context manager
    mock_conn = AsyncMock()
    mock_engine.begin.return_value.__aenter__.return_value = mock_conn

    with patch("app.core.database.logger") as mock_logger:
        # Call the function
        await init_db()

        # Assert logger calls
        mock_logger.info.assert_any_call("Initializing the database.")
        mock_logger.info.assert_any_call("Database initialized successfully.")

@pytest.mark.asyncio
@patch("app.core.database.engine")
async def test_init_db_failure(mock_engine):
    # Simulate an exception when `begin` is called
    mock_engine.begin.side_effect = Exception("DB error")

    with patch("app.core.database.logger") as mock_logger:
        # Call the function
        await init_db()

        # Assert error logger call
        mock_logger.error.assert_called_with("Error initializing the database: DB error")
