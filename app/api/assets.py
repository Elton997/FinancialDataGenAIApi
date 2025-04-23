import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.core.database import SessionLocal
from app.core.models import Asset, Metric

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to provide a SQLAlchemy session."""
    async with SessionLocal() as session:
        yield session


def format_metric(metric: Metric) -> Dict[str, Any]:
    """Format a metric object into a dictionary."""
    return {
        "latest_price": metric.latest_price,
        "change_percent_24h": metric.change_percent_24h,
        "average_price_7d": metric.average_price_7d,
    }


def format_asset(asset: Asset) -> Dict[str, Any]:
    """Format an asset and its metrics into a dictionary."""
    return {
        "symbol": asset.symbol,
        "name": asset.name,
        "metrics": [format_metric(m) for m in asset.metrics] if asset.metrics else None,
    }


async def fetch_assets_with_metrics(db: AsyncSession) -> List[Asset]:
    """Fetch all assets and their metrics from the database."""
    result = await db.execute(select(Asset).options(joinedload(Asset.metrics)))
    return result.unique().scalars().all()


@router.get("/", response_model=List[Dict[str, Any]])
async def list_assets(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """API endpoint to list all assets with their associated metrics."""
    try:
        logger.info("Fetching assets along with their metrics from the database.")
        assets = await fetch_assets_with_metrics(db)
        logger.info(f"Retrieved {len(assets)} assets from the database.")
        return [format_asset(asset) for asset in assets]
    except Exception as e:
        logger.error(f"Error occurred while fetching assets: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
