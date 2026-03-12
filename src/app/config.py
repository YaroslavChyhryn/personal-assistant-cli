import logging
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "assistant.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s — %(message)s"
