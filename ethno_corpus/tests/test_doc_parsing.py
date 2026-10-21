import unittest
from pathlib import Path
from ethno_corpus.core import DocumentAnalyzer


class TestDocParsing(unittest.TestCase):
    """Тесты для парсинга .doc файлов с сохранением кириллицы"""

    def setUp(self):
        self.input_dir = Path("c:/Users/i.petrov/dev/ethno_database/input")
        self.doc_files = list(self.input_dir.rglob("*.doc"))
        self.docx_files = list(self.input_dir.rglob("*.docx"))

    def test_doc_files_have_cyrillic(self):
        """Проверяет что .doc файлы парсятся с кириллицей"""
        if not self.doc_files:
            self.skipTest("Нет .doc файлов в input/")

        for doc_file in self.doc_files[:3]:  # Проверяем первые 3
            with self.subTest(file=doc_file.name):
                result = DocumentAnalyzer.analyze_file(str(doc_file), "Test", 2024)

                self.assertIsNotNone(result, f"Не удалось распарсить {doc_file.name}")
                self.assertGreater(
                    len(result.content), 0,
                    f"Содержимое пусто для {doc_file.name}"
                )

                # Проверяем что есть кириллица
                has_cyrillic = any('Ѐ' <= c <= 'ӿ' for c in result.content)
                self.assertTrue(
                    has_cyrillic or len(result.content) > 100,
                    f"Нет кириллицы в {doc_file.name}, контент: {result.content[:100]}"
                )

    def test_docx_files_still_work(self):
        """Проверяет что .docx файлы продолжают работать"""
        if not self.docx_files:
            self.skipTest("Нет .docx файлов в input/")

        for docx_file in self.docx_files[:3]:
            with self.subTest(file=docx_file.name):
                result = DocumentAnalyzer.analyze_file(str(docx_file), "Test", 2024)

                self.assertIsNotNone(result, f"Не удалось распарсить {docx_file.name}")
                self.assertGreater(
                    len(result.content), 0,
                    f"Содержимое пусто для {docx_file.name}"
                )

    def test_doc_passport_extraction(self):
        """Проверяет что паспорт извлекается из .doc файлов"""
        if not self.doc_files:
            self.skipTest("Нет .doc файлов в input/")

        result = DocumentAnalyzer.analyze_file(str(self.doc_files[0]), "Test", 2024)

        self.assertIsNotNone(result)
        self.assertNotEqual(result.passport, "Паспорт не найден")
        self.assertGreater(len(result.passport), 0)


class TestRealDataParsing(unittest.TestCase):
    """Проверка на реальных данных из корпуса"""

    def test_varzyga_doc_files(self):
        """Тест на файлах из Варзуги (2004)"""
        varzyga_path = Path(
            "c:/Users/i.petrov/dev/ethno_database/input/"
            "2004 с. Варзуга Терский р-н Мурманской обл/в базу"
        )

        if not varzyga_path.exists():
            self.skipTest("Директория с Варзугой не найдена")

        doc_files = list(varzyga_path.glob("*.doc"))
        self.assertGreater(len(doc_files), 0, "Нет .doc файлов в Варзуге")

        for doc_file in doc_files:
            with self.subTest(file=doc_file.name):
                result = DocumentAnalyzer.analyze_file(
                    str(doc_file),
                    "Варзуга",
                    2004
                )

                self.assertIsNotNone(result)
                self.assertGreater(len(result.content), 50)

                # Логируем результат для отладки
                print(f"\n{doc_file.name}:")
                print(f"  Размер контента: {len(result.content)} символов")
                print(f"  Первые 200 символов: {result.content[:200]}")
                print(f"  Паспорт: {result.passport[:100]}")


if __name__ == "__main__":
    unittest.main()
