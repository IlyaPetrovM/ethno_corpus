import unittest
from pathlib import Path
from ethno_corpus.utils import FileScanner, INPUT_DIR


class TestFileScanner(unittest.TestCase):
    """Тесты для сканирования документов"""

    def setUp(self):
        self.scanner = FileScanner()

    def test_scan_documents_returns_list(self):
        """Сканирование должно вернуть список"""
        docs = self.scanner.scan_documents()
        self.assertIsInstance(docs, list)

    def test_documents_have_required_fields(self):
        """Каждый документ должен иметь требуемые поля"""
        docs = self.scanner.scan_documents()
        if docs:  # если есть документы
            doc = docs[0]
            required_fields = ["file_path", "file_name", "location", "year"]
            for field in required_fields:
                self.assertIn(field, doc)

    def test_documents_have_valid_paths(self):
        """Пути к документам должны быть валидными"""
        docs = self.scanner.scan_documents()
        for doc in docs:
            path = Path(doc["file_path"])
            self.assertTrue(path.exists(), f"File does not exist: {doc['file_path']}")

    def test_documents_are_supported_formats(self):
        """Документы должны быть поддерживаемых форматов"""
        docs = self.scanner.scan_documents()
        supported = {".doc", ".docx", ".txt"}
        for doc in docs:
            ext = Path(doc["file_path"]).suffix.lower()
            self.assertIn(ext, supported, f"Unsupported format: {ext}")

    def test_documents_sorted_by_year_and_location(self):
        """Документы должны быть отсортированы по году и месту"""
        docs = self.scanner.scan_documents()
        if len(docs) > 1:
            for i in range(len(docs) - 1):
                year1 = docs[i].get("year") or 0
                year2 = docs[i + 1].get("year") or 0
                self.assertGreaterEqual(year2, year1)


if __name__ == "__main__":
    unittest.main()
