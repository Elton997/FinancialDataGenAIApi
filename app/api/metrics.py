import logging
from typing import Any, AsyncGenerator, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import SessionLocal
from app.core.models import Asset, Metric
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an asynchronous database session."""
    async with SessionLocal() as session:
        yield session


async def fetch_asset_by_symbol(db: AsyncSession, symbol: str) -> Asset:
    """Fetch an asset by its symbol."""
    result = await db.execute(select(Asset).where(Asset.symbol == symbol))
    asset = result.scalar_one_or_none()
    if not asset:
        logger.warning(f"Asset {symbol} not found.")
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


async def fetch_metric_by_asset(db: AsyncSession, asset_id: int, symbol: str) -> Metric:
    """Fetch metric details by asset ID."""
    result = await db.execute(select(Metric).where(Metric.asset_id == asset_id))
    metric = result.scalar_one_or_none()
    if not metric:
        logger.warning(f"Metrics for asset {symbol} not available.")
        raise HTTPException(status_code=404, detail="Metrics not available for this asset")
    return metric


def format_metrics_response(symbol: str, metric: Metric) -> Dict[str, Any]:
    """Format the metric information for API response."""
    return {
        "symbol": symbol,
        "latest_price": metric.latest_price,
        "change_percent_24h": metric.change_percent_24h,
        "average_price_7d": metric.average_price_7d,
    }


@router.get("/{symbol}", response_model=Dict[str, Any])
async def get_metrics(symbol: str, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """API endpoint to fetch metrics for a given asset symbol."""
    try:
        logger.info(f"Fetching metrics for asset: {symbol}")
        asset = await fetch_asset_by_symbol(db, symbol)
        metric = await fetch_metric_by_asset(db, asset.id, symbol)
        logger.info(f"Metrics for asset {symbol} retrieved successfully.")
        return format_metrics_response(symbol, metric)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving metrics for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
