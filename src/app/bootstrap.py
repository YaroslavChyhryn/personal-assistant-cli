import logging

from sqlmodel import SQLModel, inspect

from app.config import DATA_DIR, LOG_FORMAT, LOG_LEVEL

from app.db import engine

# Import models so SQLModel registers them before create_all
import app.domain.models  # noqa: F401

logger = logging.getLogger(__name__)


def init_logging() -> None:
    logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)


def init_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)
    logger.info("Database connected: %s", engine.url)

    table_names = inspect(engine).get_table_names()
    logger.info("Tables: %s", ", ".join(table_names) if table_names else "(none)")


def bootstrap() -> None:
    init_logging()
    logger.info("Starting Personal Assistant...")
    init_db()
    logger.info("Personal Assistant ready")
