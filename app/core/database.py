import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
logging.basicConfig(level=logging.INFO)
# Configure logger
logger = logging.getLogger(__name__)

# SQLite connection URL for async
DATABASE_URL: str = "sqlite+aiosqlite:///./financial_data.db"

# Create the async engine and session factory
engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal: sessionmaker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Declarative base for models
Base = declarative_base()


def get_engine() -> AsyncEngine:
    """
    Returns the database engine.
    """
    return engine


def get_session_local() -> sessionmaker:
    """
    Returns the session maker.
    """
    return SessionLocal


def get_base() -> declarative_base:
    """
    Returns the declarative base class for models.
    """
    return Base


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async generator to provide a database session.
    """
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """
    Initialize the database and create tables.
    """
    try:
        logger.info("Initializing the database.")

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing the database: {e}")
