import logging
from fastapi import FastAPI
from fastapi.routing import APIRouter
from app.api import assets, metrics, compare, summary, ingest, clear_db
from app.core.database import init_db
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """
    Creates and configures the FastAPI application.

    Returns:
        Configured FastAPI app.
    """
    app = FastAPI(title="Financial Data Aggregator & Insights Engine")

    register_event_handlers(app)
    register_routers(app)

    return app


def register_event_handlers(app: FastAPI) -> None:
    """
    Register FastAPI startup and shutdown events.

    Args:
        app: The FastAPI application.
    """
    @app.on_event("startup")
    async def startup_event() -> None:
        try:
            await init_db()
            logger.info("Database initialized successfully during startup.")
        except Exception as e:
            logger.error(f"Error during database initialization: {e}")
            raise RuntimeError("Failed to initialize database.")


def register_routers(app: FastAPI) -> None:
    """
    Register API routers with the FastAPI application.

    Args:
        app: The FastAPI application.
    """
    routers: list[tuple[APIRouter, str, list[str]]] = [
        (ingest.router, "/ingest", ["Ingest"]),
        (assets.router, "/assets", ["Assets"]),
        (metrics.router, "/metrics", ["Metrics"]),
        (compare.router, "/compare", ["Compare"]),
        (summary.router, "/summary", ["Summary"]),
        (clear_db.router, "/clear_db", ["Database"]),
    ]

    for router, prefix, tags in routers:
        app.include_router(router, prefix=prefix, tags=tags)


app = create_app()

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting the application...")

    try:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except Exception as e:
        logger.error(f"Error starting the application: {e}")
