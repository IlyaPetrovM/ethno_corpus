import shutil
from pathlib import Path
from typing import List, Optional
from whoosh.fields import Schema, ID, TEXT, NUMERIC, DATETIME
from whoosh.index import create_in, open_dir, exists_in, EmptyIndexError
from whoosh.analysis import SimpleAnalyzer, StemmingAnalyzer
from whoosh.qparser import QueryParser
from ..utils.logger import get_logger
from ..utils.config import INDEX_DIR
from ..data import Document

logger = get_logger(__name__)


class IndexBuilder:
    """Строит и управляет индексом Whoosh для полнотекстового поиска"""

    SCHEMA = Schema(
        doc_id=ID(stored=True, unique=True),
        file_name=TEXT(stored=True),
        content=TEXT(analyzer=SimpleAnalyzer()),  # Русский текст
        location=TEXT(stored=True),
        year=NUMERIC(stored=True),
        passport=TEXT(stored=True, field_boost=2.0),  # Паспорт приоритетнее
    )

    def __init__(self, index_dir: Path = INDEX_DIR):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(exist_ok=True)

    def build_index(self, documents: List[Document]) -> int:
        """Строит индекс из списка документов. Перезаписывает существующий."""
        logger.info(f"Building index from {len(documents)} documents...")

        # Удаляем старый индекс если существует
        if exists_in(str(self.index_dir)):
            logger.info("Clearing existing index")
            lock_file = self.index_dir / "MAIN_WRITELOCK"
            if lock_file.exists():
                lock_file.unlink()
            shutil.rmtree(self.index_dir)
            self.index_dir.mkdir()

        # Создаем новый индекс
        index = create_in(str(self.index_dir), self.SCHEMA)
        writer = index.writer()

        indexed_count = 0
        for doc in documents:
            try:
                writer.add_document(
                    doc_id=str(doc.id) if doc.id else doc.file_path,
                    file_name=doc.file_name,
                    content=doc.content,
                    location=doc.location or "",
                    year=doc.year or 0,
                    passport=doc.passport or ""
                )
                indexed_count += 1
            except Exception as e:
                logger.error(f"Error indexing {doc.file_path}: {e}")

        writer.commit()
        logger.info(f"Index built successfully: {indexed_count} documents")
        return indexed_count

    def search(self, query_text: str, limit: int = 100) -> List[dict]:
        """Ищет в индексе, возвращает результаты"""
        if not exists_in(str(self.index_dir)):
            logger.warning("Index does not exist")
            return []

        try:
            index = open_dir(str(self.index_dir))
            with index.searcher() as searcher:
                # Ищем в полнотекстовом поле
                query_parser = QueryParser("content", index.schema)
                query = query_parser.parse(query_text)

                results = []
                for hit in searcher.search(query, limit=limit):
                    results.append({
                        "doc_id": hit["doc_id"],
                        "file_name": hit["file_name"],
                        "location": hit.get("location", ""),
                        "year": hit.get("year", 0),
                        "passport": hit.get("passport", ""),
                        "score": hit.score
                    })

                logger.info(f"Found {len(results)} results for '{query_text}'")
                return results

        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def index_exists(self) -> bool:
        """Проверяет, существует ли индекс"""
        return exists_in(str(self.index_dir))

    def clear_index(self):
        """Очищает индекс"""
        if self.index_dir.exists():
            shutil.rmtree(self.index_dir)
            self.index_dir.mkdir()
            logger.info("Index cleared")


__all__ = ["IndexBuilder"]
