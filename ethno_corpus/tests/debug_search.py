#!/usr/bin/env python3
"""Скрипт отладки поиска и индекса"""

from pathlib import Path
from ethno_corpus.core.index_builder import IndexBuilder
from ethno_corpus.data import Document

# Путь к индексу
index_dir = Path("process/whoosh_index")
print(f"Index directory: {index_dir}")
print(f"Index exists: {index_dir.exists()}")

if index_dir.exists():
    print(f"\nFiles in index dir:")
    for f in index_dir.iterdir():
        print(f"  - {f.name}")

# Создаем builder
builder = IndexBuilder(index_dir)

# Проверяем существует ли индекс
if builder.index_exists():
    print("\n[OK] Index exists")

    # Пытаемся поискать простой запрос
    test_queries = ["синегорье", "пришел", "интервью", "документ", "текст"]

    for query in test_queries:
        results = builder.search(query)
        print(f"  Query '{query}': {len(results)} results")
        if results:
            for r in results[:2]:
                print(f"    - {r['file_name']}: score={r['score']}")
else:
    print("\n[FAIL] Index does not exist")

print("\nDone!")
