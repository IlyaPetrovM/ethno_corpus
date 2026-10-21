from typing import List, Optional
from .index_builder import IndexBuilder
from .morphology import Morphology
from ..utils.logger import get_logger
from ..utils.config import INDEX_DIR
from ..data import SearchResult, DatabaseManager
from ..utils.config import DB_PATH

logger = get_logger(__name__)


class SearchEngine:
    """Поисковый движок с морфологией"""

    def __init__(self, index_dir=INDEX_DIR, db_path=DB_PATH):
        self.index_builder = IndexBuilder(index_dir)
        self.db = DatabaseManager(db_path)
        self.morphology = Morphology()

    def search(self, query: str, limit: int = 100, context_words: int = 20) -> List[dict]:
        """Выполняет поиск с морфологией"""
        if not query.strip():
            return []

        logger.info(f"Search query: {query}")

        # Нормализуем запрос
        normalized_words = self.morphology.normalize_query(query)
        if not normalized_words:
            return []

        # Ищем в индексе Whoosh
        index_results = self.index_builder.search(query, limit=limit)

        # Обогащаем результаты контекстом
        search_results = []
        for result in index_results:
            doc_id = result["doc_id"]

            # Получаем полный документ из БД
            doc = self.db.get_document(int(doc_id) if doc_id.isdigit() else 1)
            if not doc:
                continue

            # Ищем совпадения в контексте
            contexts = self.morphology.find_in_context(
                normalized_words,
                doc.content,
                context_words
            )

            # Для каждого найденного контекста создаем результат
            for ctx in contexts:
                highlighted_context = self.morphology.highlight_word(
                    ctx["context"],
                    ctx["word"]
                )

                search_results.append({
                    "file_name": result["file_name"],
                    "file_path": doc.file_path,
                    "location": result["location"],
                    "year": result["year"],
                    "passport": result["passport"],
                    "context": highlighted_context,
                    "snippet_start": ctx["context_start"],
                    "snippet_end": ctx["context_end"],
                    "word_position": ctx["position"],
                    "score": result["score"]
                })

        logger.info(f"Found {len(search_results)} results")
        return search_results[:limit]

    def get_search_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """Возвращает подсказки для поиска"""
        words = self.morphology.normalize_query(query)
        if not words:
            return []

        # Для каждого слова ищем похожие в индексе
        # (Упрощенная версия)
        return words


__all__ = ["SearchEngine"]
