import unittest
from ethno_corpus.core import Morphology


class TestMorphology(unittest.TestCase):
    """Тесты для морфологического анализа"""

    def setUp(self):
        self.morph = Morphology()

    def test_prefix_matching(self):
        """Поиск по префиксам"""
        text = "приехал приходил привет приносит"
        matches = self.morph.find_prefix_matches("при", text)

        self.assertGreater(len(matches), 0)
        self.assertIn("приехал", matches)
        self.assertIn("приходил", matches)

    def test_similarity_identical_words(self):
        """Похожесть одинаковых слов"""
        similarity = self.morph.similarity("привет", "привет")
        self.assertEqual(similarity, 1.0)

    def test_similarity_different_words(self):
        """Похожесть разных слов"""
        similarity = self.morph.similarity("кот", "дом")
        self.assertLess(similarity, 0.5)

    def test_similarity_similar_words(self):
        """Похожесть похожих слов"""
        similarity = self.morph.similarity("пришел", "пришла")
        self.assertGreater(similarity, 0.7)

    def test_find_similar_words(self):
        """Поиск похожих слов"""
        text = "пришел пришла пришли приход"
        similar = self.morph.find_similar_words("пришел", text, min_similarity=0.75)

        self.assertGreater(len(similar), 0)
        self.assertIn("пришла", similar)

    def test_find_in_context(self):
        """Поиск с контекстом"""
        text = "У него было два кота и три собаки в доме"
        results = self.morph.find_in_context(["кота"], text, context_words=3)

        self.assertGreater(len(results), 0)
        self.assertIn("кота", results[0]["word"].lower())
        self.assertIn("context", results[0])  # есть поле context

    def test_normalize_query(self):
        """Нормализация поискового запроса"""
        query = "Привет мир!"
        normalized = self.morph.normalize_query(query)

        self.assertEqual(len(normalized), 2)
        self.assertIn("привет", normalized)
        self.assertIn("мир", normalized)

    def test_highlight_word(self):
        """Подсвечивание слова"""
        context = "The quick brown fox"
        highlighted = self.morph.highlight_word(context, "quick")

        self.assertIn("[quick]", highlighted)

    def test_context_words_limit(self):
        """Ограничение количества слов контекста"""
        text = "один два три четыре пять шесть семь восемь девять десять"
        results = self.morph.find_in_context(["пять"], text, context_words=2)

        self.assertGreater(len(results), 0)
        # Контекст должен содержать не более 5 слов (2 + ключевое + 2)
        context_word_count = len(results[0]["context"].split())
        self.assertLessEqual(context_word_count, 6)


if __name__ == "__main__":
    unittest.main()
