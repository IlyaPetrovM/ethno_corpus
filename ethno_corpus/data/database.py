import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from .models import Document
from ..utils.logger import get_logger
from ..utils.config import DB_PATH

logger = get_logger(__name__)


class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Инициализирует схему БД"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                content TEXT NOT NULL,
                location TEXT,
                year INTEGER,
                passport TEXT,
                analyzed_at DATETIME,
                file_modified_at DATETIME
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")

    def add_document(self, doc: Document) -> int:
        """Добавляет или обновляет документ в БД"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO documents
            (file_path, file_name, content, location, year, passport, analyzed_at, file_modified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            doc.file_path,
            doc.file_name,
            doc.content,
            doc.location,
            doc.year,
            doc.passport,
            doc.analyzed_at or datetime.now(),
            doc.file_modified_at
        ))

        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doc_id

    def get_document(self, doc_id: int) -> Optional[Document]:
        """Получает документ по ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return Document(
            id=row[0],
            file_path=row[1],
            file_name=row[2],
            content=row[3],
            location=row[4],
            year=row[5],
            passport=row[6],
            analyzed_at=row[7],
            file_modified_at=row[8]
        )

    def get_all_documents(self) -> List[Document]:
        """Получает все документы"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM documents")
        rows = cursor.fetchall()
        conn.close()

        return [
            Document(
                id=row[0],
                file_path=row[1],
                file_name=row[2],
                content=row[3],
                location=row[4],
                year=row[5],
                passport=row[6],
                analyzed_at=row[7],
                file_modified_at=row[8]
            )
            for row in rows
        ]

    def clear_all(self):
        """Очищает все документы"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM documents")
        conn.commit()
        conn.close()
        logger.info("Database cleared")


__all__ = ["DatabaseManager"]
