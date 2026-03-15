import logging
from pathlib import Path

DATA_DIR = Path.home() / ".assistant"
DB_PATH = DATA_DIR / "assistant.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s — %(message)s"
