from typing import Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PassportExtractor:
    """Извлекает паспорт интервью из документа"""

    @staticmethod
    def extract(content: str) -> str:
        """Извлекает паспорт (первый абзац/информацию об интервью)"""
        if not content:
            return ""

        lines = content.strip().split('\n')
        passport_lines = []

        # Собираем первые непустые строки до пустой строки
        for line in lines:
            stripped = line.strip()
            if stripped:
                passport_lines.append(stripped)
            elif passport_lines:  # первая пустая строка после текста
                break

        # Ограничиваем длину паспорта (обычно первый абзац 100-500 символов)
        passport = " ".join(passport_lines)
        return passport[:1000] if passport else ""
