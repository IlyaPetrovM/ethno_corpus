import unittest
import shutil
from pathlib import Path
import tempfile
from ethno_corpus.core import IndexBuilder
from ethno_corpus.data import Document


class TestIndexBuilder(unittest.TestCase):
    """Тесты для индексирования Whoosh"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.index_dir = Path(self.temp_dir.name) / "test_index"
        self.builder = IndexBuilder(self.index_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_build_index_creates_directory(self):
        """Построение индекса создает директорию"""
        docs = [
            Document(
                id=1,
                file_path="/test/file1.txt",
                file_name="file1.txt",
                content="Test content one",
                location="Test Place",
                year=2024
            )
        ]

        self.builder.build_index(docs)
        self.assertTrue(self.index_dir.exists())

    def test_build_index_with_documents(self):
        """Построение индекса с документами"""
        docs = [
            Document(
                id=1,
                file_path="/test/file1.txt",
                file_name="file1.txt",
                content="Hello world",
                passport="First file"
            ),
            Document(
                id=2,
                file_path="/test/file2.txt",
                file_name="file2.txt",
                content="Goodbye world",
                passport="Second file"
            )
        ]

        count = self.builder.build_index(docs)
        self.assertEqual(count, 2)
        self.assertTrue(self.builder.index_exists())

    def test_search_finds_content(self):
        """Поиск находит содержимое"""
        docs = [
            Document(
                id=1,
                file_path="/test/file1.txt",
                file_name="file1.txt",
                content="The quick brown fox",
                location="Forest"
            )
        ]

        self.builder.build_index(docs)
        results = self.builder.search("quick")

        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["file_name"], "file1.txt")

    def test_search_russian_text(self):
        """Поиск в русском тексте"""
        docs = [
            Document(
                id=1,
                file_path="/test/file1.txt",
                file_name="file1.txt",
                content="Привет мир",
                location="Россия",
                year=2024
            )
        ]

        self.builder.build_index(docs)
        results = self.builder.search("привет")

        self.assertGreater(len(results), 0)

    def test_search_nonexistent_index(self):
        """Поиск в несуществующем индексе"""
        results = self.builder.search("test")
        self.assertEqual(len(results), 0)

    def test_clear_index(self):
        """Очистка индекса"""
        docs = [
            Document(
                id=1,
                file_path="/test/file1.txt",
                file_name="file1.txt",
                content="Test"
            )
        ]

        self.builder.build_index(docs)
        self.assertTrue(self.builder.index_exists())

        self.builder.clear_index()
        self.assertFalse(self.builder.index_exists())

    def test_search_result_fields(self):
        """Результаты поиска содержат все необходимые поля"""
        docs = [
            Document(
                id=1,
                file_path="/test/file1.txt",
                file_name="file1.txt",
                content="Sample content",
                location="Test Location",
                year=2024,
                passport="Test passport"
            )
        ]

        self.builder.build_index(docs)
        results = self.builder.search("sample")

        self.assertGreater(len(results), 0)
        result = results[0]
        self.assertIn("doc_id", result)
        self.assertIn("file_name", result)
        self.assertIn("location", result)
        self.assertIn("year", result)
        self.assertIn("passport", result)


if __name__ == "__main__":
    unittest.main()
