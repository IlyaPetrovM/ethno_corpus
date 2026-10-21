#!/usr/bin/env python3
import sys
from pathlib import Path

# Добавляем ethno_corpus в путь поиска
sys.path.insert(0, str(Path(__file__).parent))

from PyQt5.QtWidgets import QApplication
from ethno_corpus.ui import MainWindow
from ethno_corpus.utils import get_logger

logger = get_logger(__name__)


def main():
    logger.info("Starting application...")
    app = QApplication(sys.argv)

    # Получаем папку из параметра командной строки (если передана)
    input_dir = None
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
        logger.info(f"Input folder from command line: {input_dir}")

    window = MainWindow(input_dir=input_dir)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
