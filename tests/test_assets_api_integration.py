import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.api.assets import list_assets, Asset, Metric


@pytest.mark.asyncio
async def test_list_assets_returns_mocked_data():
    # Mock data
    mock_data = [
        {
            "symbol": "BTC-USD",
            "name": "BTC-USD",
            "metrics": [
                {
                    "latest_price": 93580.5859375,
                    "change_percent_24h": 0.15,
                    "average_price_7d": 87732.24,
                }
            ],
        },
        {
            "symbol": "ETH-USD",
            "name": "ETH-USD",
            "metrics": [
                {
                    "latest_price": 1780.375732421875,
                    "change_percent_24h": 1.31,
                    "average_price_7d": 1641.34,
                }
            ],
        },
        {
            "symbol": "TSLA",
            "name": "TSLA",
            "metrics": [
                {
                    "latest_price": 237.97000122070312,
                    "change_percent_24h": 4.6,
                    "average_price_7d": 243.88,
                }
            ],
        },
    ]

    print("Mock data prepared:", mock_data)

    # Mock Asset and Metric objects
    mock_assets = []
    for asset_dict in mock_data:
        asset = MagicMock(spec=Asset)
        asset.symbol = asset_dict["symbol"]
        asset.name = asset_dict["name"]
        asset.metrics = [
            MagicMock(
                spec=Metric,
                latest_price=metric["latest_price"],
                change_percent_24h=metric["change_percent_24h"],
                average_price_7d=metric["average_price_7d"],
            )
            for metric in asset_dict["metrics"]
        ]
        mock_assets.append(asset)

    print("Mock assets created:", mock_assets)

    # Mock SQLAlchemy query result behavior
    mock_query_result = MagicMock()
    mock_query_result.unique.return_value.scalars.return_value.all.return_value = mock_assets

    print("Mock query result set up with chained calls")

    # Mock database execute function
    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_query_result

    print("Mock database execute function configured")

    # Call the function
    response = await list_assets(db=mock_db)

    print("Function response:", response)

    # Assert the response matches the expected data
    assert response == mock_data


@pytest.mark.asyncio
async def test_list_assets_handles_exception_and_raises_http_exception():
    mock_db = AsyncMock()
    mock_db.execute.side_effect = Exception("DB access error")

    print("Mock database configured to raise exception")

    with pytest.raises(HTTPException) as exc_info:
        await list_assets(db=mock_db)

    print("Exception raised:", exc_info.value)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal Server Error"
