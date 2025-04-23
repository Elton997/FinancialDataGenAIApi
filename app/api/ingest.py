import logging
from typing import AsyncGenerator, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.services.ingestion import ingest_data
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide an asynchronous database session."""
    async with SessionLocal() as session:
        yield session


async def perform_ingestion(db: AsyncSession) -> None:
    """Trigger the ingestion service."""
    logger.info("Market data ingestion triggered.")
    await ingest_data(db)
    logger.info("Market data ingestion completed successfully.")


@router.post("/", response_model=Dict[str, str])
async def ingest_market_data(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """API endpoint to trigger market data ingestion."""
    await perform_ingestion(db)
    return {"message": "Market data ingestion triggered"}
