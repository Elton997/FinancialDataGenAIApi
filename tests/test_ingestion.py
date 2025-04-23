import pytest
from unittest.mock import patch, AsyncMock
import pandas as pd
from app.services.ingestion import fetch_asset_data, ingest_data

@pytest.mark.asyncio
@patch("app.services.ingestion.fdr.DataReader")
async def test_fetch_asset_data_success(mock_datareader):
    # Create a mock DataFrame with deterministic values
    mock_data = pd.DataFrame({
        "Close": [
            48000.0, 49000.0, 49500.0, 50000.0, 50500.0, 51000.0, 50000.0, 49000.0, 48000.0, 50000.0,
            49500.0, 50000.0, 49000.0, 48000.0, 47000.0
        ]
    })
    mock_datareader.return_value = mock_data

    # Call the function
    result = await fetch_asset_data("BTC-USD")

    # Validate the output
    assert result is not None
    assert result["symbol"]

@pytest.mark.asyncio
@patch("app.services.ingestion.fetch_asset_data")
@patch("app.services.ingestion.AsyncSession")
async def test_ingest_data(mock_session, mock_fetch_asset_data):
    # Mock fetch_asset_data to return valid data
    mock_fetch_asset_data.return_value = {
        "symbol": "BTC-USD",
        "latest_price": 50000.0,
        "change_percent_24h": 4.17,
        "average_price_7d": 49000.0,
    }

    # Mock AsyncSession behavior
    mock_session_instance = AsyncMock()
    mock_session.return_value = mock_session_instance

    # Mock query results for Asset and Metric
    async def mock_execute(query):
        class MockResult:
            def scalar_one_or_none(self):
                return None  # Simulate no existing record
        return MockResult()

    mock_session_instance.execute.side_effect = mock_execute

    # Call the function
    await ingest_data(mock_session_instance)

    # Validate that add and commit were called
    assert mock_session_instance.add.called, "Expected 'add' to have been called."
    assert mock_session_instance.commit.called, "Expected 'commit' to have been called."