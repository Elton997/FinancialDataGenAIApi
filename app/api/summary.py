import logging
from typing import Any, AsyncGenerator, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import SessionLocal
from app.core.models import Asset, Metric
from app.services.genai import generate_summary
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session as a dependency.
    """
    try:
        async with SessionLocal() as session:
            yield session
    except Exception as e:
        logger.error(f"Error occurred while accessing the database session: {e}")
        raise HTTPException(status_code=500, detail="Database session error")


async def fetch_asset_metrics(db: AsyncSession) -> List[Dict[str, Any]]:
    """
    Fetch asset metrics from the database.
    Returns a list of dicts containing symbol, change_percent_24h, and average_price_7d.
    """
    query = (
        select(Asset.symbol, Metric.change_percent_24h, Metric.average_price_7d)
        .join(Metric, Asset.id == Metric.asset_id)
    )
    result = await db.execute(query)
    rows = result.fetchall()

    if not rows:
        logger.info("No metrics found for assets.")
        return []

    logger.info(f"Retrieved metrics for {len(rows)} assets.")
    return [
        {"symbol": row[0], "change_percent_24h": row[1], "average_price_7d": row[2]}
        for row in rows
    ]


@router.get("/", response_model=Dict[str, str])
async def get_summary(db: AsyncSession = Depends(get_db)) -> Dict[str, str]:
    """
    API endpoint to generate a summary of asset metrics.
    """
    try:
        logger.info("Fetching asset metrics from the database.")
        data = await fetch_asset_metrics(db)

        if not data:
            return {"summary": "No data available to summarize."}

        summary = generate_summary(data)
        logger.info("Summary generated successfully.")
        return {"summary": summary}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error occurred while generating the summary: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
