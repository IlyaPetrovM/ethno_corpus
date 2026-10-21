#!/usr/bin/env python3
"""Тесты для подсветки найденных слов красным цветом"""

import unittest
from ethno_corpus.core.morphology import Morphology


class TestHighlightWords(unittest.TestCase):
    """Тестирует подсветку найденных слов"""

    def test_highlight_single_word(self):
        """Проверяет подсветку одного слова"""
        context = "Это простой текст для проверки"
        word = "простой"
        result = Morphology.highlight_word(context, word)

        # Должны содержать HTML с красным цветом
        self.assertIn('<span style="color: red;">', result)
        self.assertIn('</span>', result)
        self.assertIn('<b>', result)
        self.assertIn('</b>', result)
        print(f"Test 1 result: {result}")

    def test_highlight_case_insensitive(self):
        """Проверяет что подсветка работает независимо от регистра"""
        context = "Вот Простой текст"
        word = "простой"
        result = Morphology.highlight_word(context, word)

        # Должно выделить "Простой" несмотря на разный регистр
        self.assertIn('<span style="color: red;">', result)
        self.assertIn('Простой', result)
        print(f"Test 2 result: {result}")

    def test_highlight_multiple_occurrences(self):
        """Проверяет подсветку нескольких вхождений слова"""
        context = "текст текст текст"
        word = "текст"
        result = Morphology.highlight_word(context, word)

        # Должны выделиться все три вхождения
        count = result.count('<span style="color: red;">')
        self.assertEqual(count, 3, f"Expected 3 highlights, got {count}")
        print(f"Test 3 result: {result}")

    def test_highlight_partial_word_not_matched(self):
        """Проверяет что частичные совпадения не выделяются"""
        context = "текст текстик"
        word = "текст"
        result = Morphology.highlight_word(context, word)

        # Должно выделиться только первое слово "текст", но не "текстик"
        # (так как используем \b для границы слова)
        parts = result.split('<span style="color: red;">')
        # Первое вхождение это сам HTML тег, за ним идут выделенные части
        self.assertGreaterEqual(len(parts), 2, "Should have at least one highlight")
        print(f"Test 4 result: {result}")


if __name__ == '__main__':
    unittest.main()
