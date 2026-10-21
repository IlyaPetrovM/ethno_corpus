#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка exe для Windows 7+

Использование:
    python build.py

Результат: dist/ethno_corpus.exe (150-200 МБ)
"""

import subprocess
import sys
import shutil
from pathlib import Path
import io

# Исправляем кодировку вывода на Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    print("=" * 60)
    print("Сборка поисковика этнографического корпуса")
    print("=" * 60)

    # Проверяем PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller найден: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller не установлен. Установите: pip install pyinstaller")
        sys.exit(1)

    # Очищаем старые сборки
    build_dir = Path("build")
    dist_dir = Path("dist")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    print("\n[1/3] Собираю приложение...")
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "build.spec"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"✗ Ошибка при сборке:")
        print(result.stderr)
        sys.exit(1)

    print("✓ Сборка завершена")

    # Проверяем размер exe
    exe_path = dist_dir / "ethno_corpus.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n[2/3] Размер exe: {size_mb:.1f} МБ")

        if size_mb > 200:
            print(f"⚠ Размер превышает 200 МБ (целевой лимит)")
        else:
            print(f"✓ Размер в пределах лимита (<200 МБ)")
    else:
        print("✗ exe не найден")
        sys.exit(1)

    # Информация
    print(f"\n[3/3] Информация о сборке:")
    print(f"  Путь: {exe_path}")
    print(f"  Размер: {size_mb:.1f} МБ")
    print(f"\n✓ Сборка успешна!")
    print(f"\nЗапуск приложения:")
    print(f"  {exe_path}")

if __name__ == "__main__":
    main()
