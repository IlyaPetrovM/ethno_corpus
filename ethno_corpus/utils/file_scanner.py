import os
from pathlib import Path
from typing import List, Dict
from .config import INPUT_DIR, SUPPORTED_FORMATS


class FileScanner:
    @staticmethod
    def scan_documents(input_dir: Path = None) -> List[Dict[str, any]]:
        """Сканирует папку и возвращает список документов с метаданными"""
        if input_dir is None:
            input_dir = INPUT_DIR

        input_dir = Path(input_dir)
        documents = []

        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if Path(file).suffix.lower() in SUPPORTED_FORMATS:
                    file_path = Path(root) / file

                    # Извлечение года и места из пути
                    parts = file_path.relative_to(input_dir).parts
                    location = None
                    year = None

                    if len(parts) > 0:
                        folder_name = parts[0]
                        # Парсинг "2026 Синегорье" → год и место
                        for part in folder_name.split():
                            if part.isdigit():
                                year = int(part)
                                break
                        location = folder_name.replace(str(year) + " ", "") if year else folder_name

                    documents.append({
                        "file_path": str(file_path),
                        "file_name": file,
                        "location": location,
                        "year": year,
                        "rel_path": str(file_path.relative_to(input_dir))
                    })

        return sorted(documents, key=lambda x: (x.get("year") or 0, x.get("location") or ""))
