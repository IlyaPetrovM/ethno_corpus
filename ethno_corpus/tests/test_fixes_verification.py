"""
Тесты для проверки исправлений трёх критических багов:
1. WRITELOCK блокировка
2. Просмотр документа по file_path
3. PyQt5 обновление
"""

import unittest
from pathlib import Path
from ethno_corpus.data import DatabaseManager, Document
from ethno_corpus.core import IndexBuilder


class TestWriteLockFix(unittest.TestCase):
    """Проверка исправления WRITELOCK блокировки"""

    def setUp(self):
        self.index_builder = IndexBuilder()
        self.docs = [
            Document(
                id=1, file_name="test1.txt", file_path=Path("input/test1.txt"),
                content="Варзуга река Карелия", location="Карелия", year=2020, passport="Test 1"
            ),
            Document(
                id=2, file_name="test2.txt", file_path=Path("input/test2.txt"),
                content="Варзуга архив документы", location="Архив", year=2021, passport="Test 2"
            ),
        ]

    def test_build_index_twice_without_writelock_error(self):
        """Индекс должен пересстраиваться без WRITELOCK ошибок"""
        # Первая сборка
        count1 = self.index_builder.build_index(self.docs)
        self.assertEqual(count1, 2)

        # Вторая сборка (без ошибок)
        count2 = self.index_builder.build_index(self.docs)
        self.assertEqual(count2, 2)

    def test_search_after_rebuild(self):
        """Поиск должен работать после перестройки индекса"""
        self.index_builder.build_index(self.docs)
        self.index_builder.build_index(self.docs)  # Пересборка

        results = self.index_builder.search("Варзуга")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["file_name"], "test1.txt")


class TestDocumentViewingFix(unittest.TestCase):
    """Проверка исправления просмотра документа по file_path"""

    def setUp(self):
        self.db = DatabaseManager()
        self.db.clear_all()

        self.docs = [
            Document(
                id=1, file_name="doc1.txt", file_path="input/doc1.txt",
                content="Content 1", location="Place 1", year=2020, passport="Passport 1"
            ),
            Document(
                id=2, file_name="doc2.txt", file_path="input/doc2.txt",
                content="Content 2", location="Place 2", year=2021, passport="Passport 2"
            ),
        ]

        for doc in self.docs:
            doc.id = self.db.add_document(doc)

    def test_find_document_by_file_path(self):
        """Документ должен находиться по file_path"""
        all_docs = self.db.get_all_documents()

        # Ищем по file_path как в исправленном коде
        test_file_path = "input/doc1.txt"
        found_doc = None
        for d in all_docs:
            if str(d.file_path) == str(test_file_path):
                found_doc = d
                break

        self.assertIsNotNone(found_doc)
        self.assertEqual(found_doc.file_name, "doc1.txt")
        self.assertEqual(found_doc.passport, "Passport 1")

    def test_get_all_documents_has_required_fields(self):
        """get_all_documents должен возвращать docs с file_path"""
        all_docs = self.db.get_all_documents()

        for doc in all_docs:
            self.assertIsNotNone(doc.file_path)
            self.assertIsNotNone(doc.file_name)
            self.assertIsNotNone(doc.content)


class TestPyQt5Update(unittest.TestCase):
    """Проверка обновления PyQt5"""

    def test_pyqt5_import(self):
        """PyQt5 должен импортироваться корректно"""
        try:
            from PyQt5.QtWidgets import QApplication, QMainWindow
            from PyQt5.QtCore import Qt
            success = True
        except ImportError:
            success = False

        self.assertTrue(success, "PyQt5 импорт не работает")

    def test_no_pyqt6_in_requirements(self):
        """requirements.txt не должен содержать PyQt6"""
        with open("requirements.txt", "r") as f:
            content = f.read()
            self.assertNotIn("PyQt6", content)
            self.assertIn("PyQt5", content)

    def test_no_pyqt6_in_build_spec(self):
        """build.spec не должен содержать PyQt6"""
        with open("build.spec", "r") as f:
            content = f.read()
            self.assertNotIn("'PyQt6", content)
            self.assertIn("'PyQt5", content)


if __name__ == "__main__":
    unittest.main()
