"""
Тесты поиска с реальными фрагментами из .docx документов
Задача: Проверить что поиск находит реальный контент из документов
"""

import unittest
import json
from pathlib import Path
from ethno_corpus.core.index_builder import IndexBuilder
from ethno_corpus.data import Document

SAMPLES_FILE = Path(__file__).parent / "docx_samples.json"


class TestSearchWithRealDocxData(unittest.TestCase):
    """Тестирует поиск с реальными текстами из .docx файлов"""

    @classmethod
    def setUpClass(cls):
        """Подготавливает индекс с реальными данными из .docx"""
        if not SAMPLES_FILE.exists():
            raise FileNotFoundError(f"Samples file not found: {SAMPLES_FILE}")

        with open(SAMPLES_FILE, "r", encoding="utf-8") as f:
            samples = json.load(f)

        # Создаем документы из образцов
        cls.docs = []
        cls.test_data = {}  # Сохраняем для проверок

        for idx, (filename, info) in enumerate(samples.items(), 1):
            # Весь контент = все фрагменты вместе
            content = "\n".join(info["fragments"])

            doc = Document(
                id=idx,
                file_name=filename,
                file_path=Path(info["rel_path"]),
                content=content,
                location="Синегорье",
                year=2027,
                passport=info["fragments"][0]
            )
            cls.docs.append(doc)
            cls.test_data[filename] = info

        # Строим индекс
        cls.index_builder = IndexBuilder()
        count = cls.index_builder.build_index(cls.docs)
        print(f"\nBuilt index with {count} documents")

    # ===== БАЗОВЫЕ ТЕСТЫ =====

    def test_01_search_finds_results_for_location(self):
        """Поиск 'Синегорье' должен найти документы"""
        results = self.index_builder.search("Синегорье")
        self.assertGreater(len(results), 0, "Should find 'Синегорье'")

    def test_02_search_finds_informant_word(self):
        """Поиск 'Информант' должен найти документы"""
        results = self.index_builder.search("Информант")
        self.assertGreater(len(results), 0, "Should find 'Информант'")

    def test_03_search_finds_collector_word(self):
        """Поиск 'Собиратели' должен найти документы"""
        results = self.index_builder.search("Собиратели")
        self.assertGreater(len(results), 0, "Should find 'Собиратели'")

    # ===== ТЕСТЫ НА КОНКРЕТНЫЕ ИМЕНА =====

    def test_10_search_finds_name_trufakina(self):
        """Поиск 'Труфакина' должен найти документ с этим информантом"""
        results = self.index_builder.search("Труфакина")
        self.assertGreater(len(results), 0, "Should find 'Труфакина'")

    def test_11_search_finds_name_burov(self):
        """Поиск 'Буров' должен найти документ"""
        results = self.index_builder.search("Буров")
        self.assertGreater(len(results), 0, "Should find 'Буров'")

    def test_12_search_finds_name_tamara(self):
        """Поиск 'Тамара' должен найти документ"""
        results = self.index_builder.search("Тамара")
        self.assertGreater(len(results), 0, "Should find 'Тамара'")

    # ===== ТЕСТЫ НА ГЛАГОЛЫ И СУЩЕСТВИТЕЛЬНЫЕ =====

    def test_20_search_finds_verb_worked(self):
        """Поиск 'работала' должен найти документы"""
        results = self.index_builder.search("работала")
        self.assertGreater(len(results), 0, "Should find 'работала'")

    def test_21_search_finds_noun_teacher(self):
        """Поиск 'учительницей' должен найти документы"""
        results = self.index_builder.search("учительницей")
        self.assertGreater(len(results), 0, "Should find 'учительницей'")

    def test_22_search_finds_noun_school(self):
        """Поиск 'школе' должен найти документы"""
        results = self.index_builder.search("школе")
        self.assertGreater(len(results), 0, "Should find 'школе'")

    # ===== ТЕСТЫ НА СПЕЦИФИЧЕСКИЕ СЛОВА =====

    def test_30_search_finds_kolyading(self):
        """Поиск 'колядовали' должен найти документ"""
        results = self.index_builder.search("колядовали")
        self.assertGreater(len(results), 0, "Should find 'колядовали'")

    def test_31_search_finds_strawberry(self):
        """Поиск 'земляникой' должен найти документ"""
        results = self.index_builder.search("земляникой")
        self.assertGreater(len(results), 0, "Should find 'земляникой'")

    def test_32_search_finds_river(self):
        """Поиск 'Речка' должен найти документ"""
        results = self.index_builder.search("Речка")
        self.assertGreater(len(results), 0, "Should find 'Речка'")

    def test_33_search_finds_village_name(self):
        """Поиск 'Липовка' должен найти документ"""
        results = self.index_builder.search("Липовка")
        self.assertGreater(len(results), 0, "Should find 'Липовка'")

    def test_34_search_finds_new_text(self):
        """Поиск 'новички' должен найти документ"""
        results = self.index_builder.search("новички")
        self.assertGreater(len(results), 0, "Should find 'новички'")

    # ===== ТЕСТЫ НА СТРУКТУРУ РЕЗУЛЬТАТОВ =====

    def test_40_search_results_have_correct_structure(self):
        """Результаты должны содержать необходимые поля"""
        results = self.index_builder.search("Синегорье")
        self.assertGreater(len(results), 0)

        for result in results:
            self.assertIn("doc_id", result)
            self.assertIn("file_name", result)
            self.assertIn("location", result)
            self.assertIn("year", result)

    def test_41_search_returns_scores(self):
        """Результаты должны содержать релевантность (score)"""
        results = self.index_builder.search("Синегорье")
        self.assertGreater(len(results), 0)

        for result in results:
            self.assertIn("score", result)
            self.assertGreater(result["score"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
