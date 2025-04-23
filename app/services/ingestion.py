import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

import FinanceDataReader as fdr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.models import Asset, Metric
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_date_range(days_back: int = 15) -> tuple[str, str]:
    """
    Get a start and end date string in 'YYYY-MM-DD' format.
    """
    end_date = datetime.now() + timedelta(days=1)
    start_date = end_date - timedelta(days=days_back)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


async def fetch_asset_data(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Fetch asset data using FinanceDataReader and calculate metrics.

    Args:
        symbol: The symbol of the asset to fetch data for.

    Returns:
        A dictionary with metrics or None if data is not available.
    """
    try:
        logger.info(f"Fetching data for {symbol}...")
        start_date, end_date = get_date_range()
        data = fdr.DataReader(symbol, start=start_date, end=end_date)

        if data.empty:
            logger.warning(f"No data found for {symbol}.")
            return None

        latest_price = data["Close"].iloc[-1]
        change_percent_24h = ((latest_price - data["Close"].iloc[-2]) / data["Close"].iloc[-2]) * 100
        average_price_7d = data["Close"].iloc[-7:].mean()

        return {
            "symbol": symbol,
            "latest_price": latest_price,
            "change_percent_24h": round(change_percent_24h, 2),
            "average_price_7d": round(average_price_7d, 2),
        }
    except Exception as e:
        logger.error(f"Error fetching data for {symbol}: {e}")
        return None


async def upsert_asset(session: AsyncSession, symbol: str) -> Asset:
    """
    Insert asset into database if not exists and return the asset.

    Args:
        session: Active database session.
        symbol: Asset symbol.

    Returns:
        Asset instance.
    """
    result = await session.execute(select(Asset).where(Asset.symbol == symbol))
    asset = result.scalar_one_or_none()

    if not asset:
        asset = Asset(symbol=symbol, name=symbol)
        session.add(asset)
        await session.commit()
        logger.info(f"Asset {symbol} added to the database.")

    return asset


async def upsert_metric(session: AsyncSession, asset_id: int, metrics: Dict[str, float]) -> None:
    """
    Insert or update metrics in the database.

    Args:
        session: Active database session.
        asset_id: Foreign key reference to the asset.
        metrics: Dictionary containing metric values.
    """
    result = await session.execute(select(Metric).where(Metric.asset_id == asset_id))
    existing_metric = result.scalar_one_or_none()

    if existing_metric:
        existing_metric.latest_price = metrics["latest_price"]
        existing_metric.change_percent_24h = metrics["change_percent_24h"]
        existing_metric.average_price_7d = metrics["average_price_7d"]
        logger.info(f"Metric data for asset ID {asset_id} updated.")
    else:
        new_metric = Metric(
            asset_id=asset_id,
            latest_price=metrics["latest_price"],
            change_percent_24h=metrics["change_percent_24h"],
            average_price_7d=metrics["average_price_7d"],
        )
        session.add(new_metric)
        logger.info(f"Metric data for asset ID {asset_id} added.")

    await session.commit()


async def ingest_data(session: AsyncSession, symbols: List[str] = ["BTC-USD", "ETH-USD", "TSLA"]) -> None:
    """
    Ingest asset metrics into the database.

    Args:
        session: Active database session.
        symbols: List of asset symbols to ingest.
    """
    for symbol in symbols:
        retries: int = 3
        while retries > 0:
            try:
                data = await fetch_asset_data(symbol)

                if data is None:
                    break

                asset = await upsert_asset(session, symbol)
                await upsert_metric(session, asset.id, data)

                break  # Success, break retry loop
            except Exception as e:
                retries -= 1
                logger.error(f"Error processing {symbol}: {e}. Retries left: {retries}")
                if retries == 0:
                    logger.warning(f"Failed to process {symbol} after retries.")
                await session.commit()
