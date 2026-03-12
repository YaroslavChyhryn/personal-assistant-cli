import logging
from collections.abc import Generator

from sqlmodel import Session, create_engine

from app.config import DATABASE_URL

logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL, echo=False)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session and close it when done."""
    with Session(engine) as session:
        yield session
