from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Document:
    id: Optional[int] = None
    file_path: str = ""
    file_name: str = ""
    content: str = ""
    location: Optional[str] = None
    year: Optional[int] = None
    passport: Optional[str] = None
    analyzed_at: Optional[datetime] = None
    file_modified_at: Optional[datetime] = None


@dataclass
class SearchResult:
    document_id: int
    file_name: str
    location: Optional[str]
    year: Optional[int]
    passport: str
    context: str  # текст с подсвеченными словами
    snippet_start: int
    snippet_end: int
