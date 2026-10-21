import os
from pathlib import Path
from datetime import datetime
from typing import Optional
from docx import Document as DocxDocument
from ..utils.logger import get_logger
from ..data import Document

logger = get_logger(__name__)


class DocumentAnalyzer:
    """Анализирует и парсит документы разных форматов"""

    @staticmethod
    def analyze_file(file_path: str, location: Optional[str] = None, year: Optional[int] = None) -> Optional[Document]:
        """Анализирует файл и возвращает Document с содержимым"""
        path = Path(file_path)

        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None

        try:
            suffix = path.suffix.lower()

            if suffix == ".docx":
                content = DocumentAnalyzer._parse_docx(file_path)
            elif suffix == ".doc":
                content = DocumentAnalyzer._parse_doc(file_path)
            elif suffix == ".txt":
                content = DocumentAnalyzer._parse_txt(file_path)
            else:
                logger.warning(f"Unsupported format: {suffix}")
                return None

            if not content:
                logger.warning(f"Could not extract content from: {file_path}")
                return None

            # Извлекаем паспорт (первый абзац)
            passport = DocumentAnalyzer._extract_passport(content)

            # Получаем дату модификации файла
            file_modified_at = datetime.fromtimestamp(path.stat().st_mtime)

            doc = Document(
                file_path=file_path,
                file_name=path.name,
                content=content,
                location=location,
                year=year,
                passport=passport,
                file_modified_at=file_modified_at
            )

            logger.info(f"Analyzed: {file_path} ({len(content)} chars)")
            return doc

        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return None

    @staticmethod
    def _parse_docx(file_path: str) -> str:
        """Парсит .docx файл"""
        try:
            doc = DocxDocument(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n".join(paragraphs)
        except Exception as e:
            logger.error(f"Error parsing DOCX {file_path}: {e}")
            return ""

    @staticmethod
    def _parse_doc(file_path: str) -> str:
        """Парсит .doc файл через конвертацию в .docx"""
        try:
            from doc2docx import convert
            import tempfile
            from pathlib import Path as PathlibPath

            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
                tmp_docx_path = tmp.name

            try:
                # Конвертируем .doc в .docx
                convert(file_path, tmp_docx_path)

                # Читаем конвертированный файл
                content = DocumentAnalyzer._parse_docx(tmp_docx_path)

                return content
            finally:
                # Удаляем временный файл
                try:
                    PathlibPath(tmp_docx_path).unlink()
                except:
                    pass

        except Exception as e:
            logger.warning(f"Could not parse DOC {file_path} with doc2docx: {e}")
            return DocumentAnalyzer._parse_doc_fallback(file_path)

    @staticmethod
    def _parse_doc_fallback(file_path: str) -> str:
        """Fallback для .doc файлов - попытка декодирования с поддержкой кириллицы"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                text = ""
                i = 0

                while i < len(content):
                    byte = content[i]

                    # ASCII
                    if byte < 32:
                        if byte in (9, 10, 13):  # Tab, LF, CR
                            text += chr(byte)
                    elif byte < 127:
                        text += chr(byte)
                    # UTF-8 многобайтовые символы (включая кириллицу)
                    elif byte >= 192 and byte <= 239:
                        try:
                            for end in range(i + 1, min(i + 4, len(content))):
                                try:
                                    decoded = content[i:end+1].decode('utf-8')
                                    text += decoded
                                    i = end
                                    break
                                except:
                                    continue
                        except:
                            pass

                    i += 1

                return text[:50000] if text else ""
        except Exception as e:
            logger.error(f"Fallback parsing failed for {file_path}: {e}")
            return ""

    @staticmethod
    def _parse_txt(file_path: str) -> str:
        """Парсит .txt файл"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error parsing TXT {file_path}: {e}")
            return ""

    @staticmethod
    def _extract_passport(content: str) -> str:
        """Извлекает паспорт интервью (первый абзац)"""
        lines = content.split('\n')
        passport_lines = []

        for line in lines:
            if line.strip():
                passport_lines.append(line.strip())
            elif passport_lines:
                break

        passport = " ".join(passport_lines)[:500]
        return passport if passport else "Паспорт не найден"


__all__ = ["DocumentAnalyzer"]
