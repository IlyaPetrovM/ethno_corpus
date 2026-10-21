#!/usr/bin/env python3
"""Интеграционный тест для подсветки результатов поиска"""

import unittest
from ethno_corpus.core.morphology import Morphology


class TestSearchHighlighting(unittest.TestCase):
    """Тестирует подсветку найденных слов в результатах поиска"""

    def test_highlight_returns_html_with_red_color(self):
        """Проверяет что highlight_word возвращает HTML с красным цветом"""
        context = "Это текст для проверки"
        word = "текст"
        result = Morphology.highlight_word(context, word)

        # Должны быть HTML теги для красного цвета и жирного текста
        self.assertIn('style="color: red;"', result)
        self.assertIn('<b>', result)
        self.assertIn('</b>', result)
        self.assertIn('<span', result)
        self.assertIn('</span>', result)
        print(f"[OK] HTML highlighting: {result}")

    def test_highlight_case_insensitive(self):
        """Проверяет что поиск не зависит от регистра"""
        context = "Большой текст"
        word = "большой"
        result = Morphology.highlight_word(context, word)

        self.assertIn('style="color: red;"', result)
        # Исходный текст "Большой" должен остаться с той же капитализацией
        self.assertIn('Большой', result)
        print(f"[OK] Case-insensitive search: {result}")

    def test_highlight_all_occurrences(self):
        """Проверяет что все вхождения выделяются"""
        context = "как как как"
        word = "как"
        result = Morphology.highlight_word(context, word)

        # Должны быть три span'а с красным цветом
        count = result.count('style="color: red;"')
        self.assertEqual(count, 3, f"Ожидалось 3 выделения, получено {count}")
        print(f"[OK] All occurrences highlighted: {result}")

    def test_hpluv_color_generation(self):
        """Проверяет что HPLuv генерирует валидные цвета"""
        from hsluv import hpluv_to_rgb

        # Тестируем несколько случайных hue значений
        test_hues = [0, 90, 180, 270]
        for hue in test_hues:
            r, g, b = hpluv_to_rgb([hue, 100, 95])

            # RGB должны быть в диапазоне [0, 1]
            self.assertGreaterEqual(r, 0)
            self.assertLessEqual(r, 1)
            self.assertGreaterEqual(g, 0)
            self.assertLessEqual(g, 1)
            self.assertGreaterEqual(b, 0)
            self.assertLessEqual(b, 1)

            # Преобразуем в HEX
            hex_color = "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))
            self.assertTrue(hex_color.startswith("#"))
            self.assertEqual(len(hex_color), 7)
            print(f"[OK] Hue {hue} deg -> RGB({r:.2f}, {g:.2f}, {b:.2f}) -> {hex_color}")


if __name__ == '__main__':
    unittest.main()
