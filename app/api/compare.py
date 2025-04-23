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
    """Dependency to provide a database session."""
    async with SessionLocal() as session:
        yield session


async def get_asset_by_symbol(db: AsyncSession, symbol: str) -> Asset:
    """Retrieve an Asset by its symbol."""
    result = await db.execute(select(Asset).where(Asset.symbol == symbol))
    asset = result.scalar_one_or_none()

    if not asset:
        logger.warning(f"Asset {symbol} not found.")
        raise HTTPException(status_code=404, detail=f"Asset {symbol} not found")

    return asset


async def get_metric_by_asset_id(db: AsyncSession, asset_id: int, symbol: str) -> Metric:
    """Retrieve Metric data for a given Asset ID."""
    result = await db.execute(select(Metric).where(Metric.asset_id == asset_id))
    metric = result.scalar_one_or_none()

    if not metric:
        logger.warning(f"Metrics not available for asset {symbol}.")
        raise HTTPException(status_code=404, detail=f"Metrics not available for {symbol}")

    return metric


def format_metric(metric: Metric) -> Dict[str, Any]:
    """Format metric data for the response."""
    return {
        "latest_price": metric.latest_price,
        "change_percent_24h": metric.change_percent_24h,
        "average_price_7d": metric.average_price_7d,
    }


@router.get("/", response_model=Dict[str, Dict[str, Any]])
async def compare_assets(
    asset1: str,
    asset2: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Dict[str, Any]]:
    """API endpoint to compare two assets and return their metrics."""
    try:
        logger.info(f"Comparing assets: {asset1} and {asset2}.")

        metrics: Dict[str, Dict[str, Any]] = {}

        for symbol in [asset1, asset2]:
            asset = await get_asset_by_symbol(db, symbol)
            metric = await get_metric_by_asset_id(db, asset.id, symbol)
            metrics[symbol] = format_metric(metric)

        logger.info("Asset comparison successful.")
        return {
            "asset1": metrics[asset1],
            "asset2": metrics[asset2],
        }

    except HTTPException:
        raise  # Let FastAPI handle the HTTPException properly
    except Exception as e:
        logger.error(f"Error comparing assets: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
