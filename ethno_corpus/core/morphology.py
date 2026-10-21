import re
from typing import List, Tuple
from difflib import SequenceMatcher
from ..utils.logger import get_logger

logger = get_logger(__name__)


class Morphology:
    """Морфологический анализ: поиск по префиксам и похожим словам"""

    MIN_SIMILARITY = 0.8  # Порог похожести (80%)

    @staticmethod
    def find_prefix_matches(word: str, text: str) -> List[str]:
        """Находит слова в тексте, начинающиеся с префикса word"""
        pattern = r'\b' + re.escape(word.lower()) + r'\w*'
        matches = re.findall(pattern, text.lower())
        return list(set(matches))  # Уникальные слова

    @staticmethod
    def similarity(word1: str, word2: str) -> float:
        """Вычисляет похожесть двух слов (0.0 - 1.0)"""
        matcher = SequenceMatcher(None, word1.lower(), word2.lower())
        return matcher.ratio()

    @staticmethod
    def find_similar_words(word: str, text: str, min_similarity: float = 0.8) -> List[str]:
        """Находит слова в тексте, похожие на заданное слово"""
        words = re.findall(r'\b\w+\b', text.lower())
        similar = []

        for w in set(words):
            if Morphology.similarity(word.lower(), w) >= min_similarity:
                similar.append(w)

        return similar

    @staticmethod
    def find_in_context(query_words: List[str], text: str, context_words: int = 20) -> List[dict]:
        """Находит query_words в тексте с контекстом"""
        words = text.split()
        results = []
        found_positions = set()

        for i, word in enumerate(words):
            word_lower = word.lower().strip('.,!?;:')

            # Проверяем точное совпадение или префикс
            for query in query_words:
                if word_lower == query.lower() or word_lower.startswith(query.lower()):
                    if i not in found_positions:
                        found_positions.add(i)

                        # Извлекаем контекст
                        start = max(0, i - context_words)
                        end = min(len(words), i + context_words + 1)

                        context_words_list = words[start:end]
                        context = " ".join(context_words_list)

                        results.append({
                            "position": i,
                            "word": words[i],
                            "context": context,
                            "start_in_context": i - start,
                            "context_start": start,
                            "context_end": end
                        })
                    break

        return results

    @staticmethod
    def normalize_query(query: str) -> List[str]:
        """Нормализует поисковый запрос в список слов"""
        # Удаляем пунктуацию и разбиваем на слова
        words = re.findall(r'\b\w+\b', query)
        return [w.lower() for w in words if len(w) > 1]  # Слова длиной > 1 символа

    @staticmethod
    def highlight_word(context: str, word: str) -> str:
        """Подсвечивает слово в контексте (для вывода)"""
        # Подсвечиваем как [word]
        pattern = r'\b' + re.escape(word) + r'\b'
        return re.sub(pattern, f'[{word}]', context, flags=re.IGNORECASE)


__all__ = ["Morphology"]
