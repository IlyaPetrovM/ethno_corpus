import unittest
import tempfile
from pathlib import Path
from ethno_corpus.core import DocumentAnalyzer


class TestDocumentAnalyzer(unittest.TestCase):
    """Тесты для анализатора документов"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_txt_file(self):
        """Парсинг .txt файла"""
        txt_path = Path(self.temp_dir.name) / "test.txt"
        test_content = "Первый абзац\nВторой абзац\nТретий абзац"
        txt_path.write_text(test_content, encoding='utf-8')

        doc = DocumentAnalyzer.analyze_file(str(txt_path), "Test Location", 2024)

        self.assertIsNotNone(doc)
        self.assertEqual(doc.file_name, "test.txt")
        self.assertEqual(doc.location, "Test Location")
        self.assertEqual(doc.year, 2024)
        self.assertIn("Первый абзац", doc.content)

    def test_passport_extraction(self):
        """Извлечение паспорта из содержимого"""
        content = """Информант: Иван Петров, род. 1950
Место: Москва
Дата: 15 сентября 2024

Основное содержание интервью...
Много текста здесь...
"""
        doc = DocumentAnalyzer.analyze_file(
            self._create_txt_file(content),
            "Москва", 2024
        )

        self.assertIsNotNone(doc)
        self.assertIn("Иван Петров", doc.passport)

    def test_file_not_found(self):
        """Обработка несуществующего файла"""
        doc = DocumentAnalyzer.analyze_file("/nonexistent/path/file.txt")
        self.assertIsNone(doc)

    def test_unsupported_format(self):
        """Обработка неподдерживаемого формата"""
        unsupported = Path(self.temp_dir.name) / "test.xyz"
        unsupported.write_text("test")

        doc = DocumentAnalyzer.analyze_file(str(unsupported))
        self.assertIsNone(doc)

    def _create_txt_file(self, content: str) -> str:
        """Вспомогательный метод для создания txt файла"""
        path = Path(self.temp_dir.name) / "temp.txt"
        path.write_text(content, encoding='utf-8')
        return str(path)


class TestPassportExtraction(unittest.TestCase):
    """Тесты для извлечения паспорта"""

    def test_extract_first_paragraph(self):
        """Извлечение первого абзаца как паспорта"""
        from ethno_corpus.core import PassportExtractor

        content = """Респондент: Мария Сергеевна, р. 1952, г. Варзуга
Собеседники: Иван Иванов
Дата: 15.09.2004

Основной текст интервью начинается здесь.
И продолжается дальше.
"""
        passport = PassportExtractor.extract(content)
        self.assertIn("Мария Сергеевна", passport)

    def test_extract_empty_content(self):
        """Извлечение из пустого содержимого"""
        from ethno_corpus.core import PassportExtractor

        passport = PassportExtractor.extract("")
        self.assertEqual(passport, "")

    def test_passport_length_limit(self):
        """Ограничение длины паспорта"""
        from ethno_corpus.core import PassportExtractor

        long_passport = "А" * 2000
        passport = PassportExtractor.extract(long_passport)
        self.assertLessEqual(len(passport), 1000)


if __name__ == "__main__":
    unittest.main()
