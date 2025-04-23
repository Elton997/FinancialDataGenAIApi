import logging
from typing import AsyncGenerator, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.core.models import Asset, Metric
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
router = APIRouter()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to provide a database session."""
    async with SessionLocal() as session:
        yield session


async def clear_table_data(db: AsyncSession, model: type) -> None:
    """Delete all records from a specified table."""
    logger.info(f"Clearing data from the {model.__name__} table...")
    await db.execute(delete(model))
    await db.commit()
    logger.info(f"{model.__name__} table cleared.")


async def clear_all_data(db: AsyncSession) -> None:
    """Clear data from Metric and Asset tables in proper order."""
    try:
        await clear_table_data(db, Metric)  # Metrics first due to FK constraints
        await clear_table_data(db, Asset)
        logger.info("All data cleared successfully.")
    except Exception as e:
        logger.error(f"Error clearing data: {e}")
        raise HTTPException(status_code=500, detail="Error clearing data.")


@router.delete("/", response_model=Dict[str, str])
async def clear_db(db: AsyncSession = Depends(get_db)) -> Dict[str, str]:
    """
    API endpoint to clear all data from the Asset and Metric tables.
    """
    try:
        await clear_all_data(db)
        logger.info("Database cleared successfully via API call.")
        return {"message": "Database cleared successfully."}
    except Exception as e:
        logger.error(f"Failed to clear database: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear database.")
