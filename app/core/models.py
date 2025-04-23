import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base
logging.basicConfig(level=logging.INFO)
# Set up logger
logger = logging.getLogger(__name__)


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationship to metrics
    metrics: Mapped[List["Metric"]] = relationship("Metric", back_populates="asset")


class Metric(Base):
    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)
    latest_price: Mapped[float] = mapped_column(Float, nullable=False)
    change_percent_24h: Mapped[float] = mapped_column(Float, nullable=False)
    average_price_7d: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationship to asset
    asset: Mapped["Asset"] = relationship("Asset", back_populates="metrics")
