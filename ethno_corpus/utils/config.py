import sys
import os
from pathlib import Path

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.parent.parent

INPUT_DIR = BASE_DIR / "input"
PROCESS_DIR = BASE_DIR / "ethno_corpus_temp"
DB_PATH = PROCESS_DIR / "corpus.db"
INDEX_DIR = PROCESS_DIR / "whoosh_index"

# Создать директории если их нет
PROCESS_DIR.mkdir(exist_ok=True)
INDEX_DIR.mkdir(exist_ok=True)

SUPPORTED_FORMATS = {".doc", ".docx", ".txt"}
