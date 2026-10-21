import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
INPUT_DIR = BASE_DIR / "input"
PROCESS_DIR = BASE_DIR / "process"
OUTPUT_DIR = BASE_DIR / "output"
DB_PATH = PROCESS_DIR / "corpus.db"
INDEX_DIR = PROCESS_DIR / "whoosh_index"

# Создать директории если их нет
PROCESS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
INDEX_DIR.mkdir(exist_ok=True)

SUPPORTED_FORMATS = {".doc", ".docx", ".txt"}
