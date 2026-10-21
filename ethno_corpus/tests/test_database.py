import unittest
import tempfile
from pathlib import Path
from datetime import datetime
from ethno_corpus.data import DatabaseManager, Document
from ethno_corpus.utils.config import PROCESS_DIR


class TestDatabaseManager(unittest.TestCase):
    """Тесты для управления БД"""

    def setUp(self):
        # Используем временную БД для тестов
        self.temp_db = Path(PROCESS_DIR) / "test_corpus.db"
        self.db = DatabaseManager(self.temp_db)

    def tearDown(self):
        # Удаляем тестовую БД
        if self.temp_db.exists():
            self.temp_db.unlink()

    def test_database_initialized(self):
        """БД должна быть инициализирована"""
        self.assertTrue(self.temp_db.exists())

    def test_add_document(self):
        """Добавление документа"""
        doc = Document(
            file_path="/path/to/file.docx",
            file_name="file.docx",
            content="Test content",
            location="Test location",
            year=2024,
            passport="Test passport"
        )
        doc_id = self.db.add_document(doc)
        self.assertIsNotNone(doc_id)
        self.assertGreater(doc_id, 0)

    def test_get_document(self):
        """Получение документа по ID"""
        doc = Document(
            file_path="/path/to/file2.docx",
            file_name="file2.docx",
            content="Test content 2",
            location="Test location 2",
            year=2023
        )
        doc_id = self.db.add_document(doc)

        retrieved = self.db.get_document(doc_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.file_name, "file2.docx")
        self.assertEqual(retrieved.content, "Test content 2")

    def test_get_all_documents(self):
        """Получение всех документов"""
        doc1 = Document(
            file_path="/path/to/file1.docx",
            file_name="file1.docx",
            content="Content 1"
        )
        doc2 = Document(
            file_path="/path/to/file2.docx",
            file_name="file2.docx",
            content="Content 2"
        )
        self.db.add_document(doc1)
        self.db.add_document(doc2)

        docs = self.db.get_all_documents()
        self.assertGreaterEqual(len(docs), 2)

    def test_clear_all(self):
        """Очистка всех документов"""
        doc = Document(
            file_path="/path/to/file.docx",
            file_name="file.docx",
            content="Test"
        )
        self.db.add_document(doc)
        self.db.clear_all()

        docs = self.db.get_all_documents()
        self.assertEqual(len(docs), 0)


if __name__ == "__main__":
    unittest.main()
