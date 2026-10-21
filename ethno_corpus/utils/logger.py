import logging
from pathlib import Path
from .config import PROCESS_DIR

LOG_FILE = PROCESS_DIR / "corpus.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def get_logger(name):
    return logging.getLogger(name)
