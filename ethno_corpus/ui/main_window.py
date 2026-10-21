from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTreeWidget, QTreeWidgetItem, QSplitter, QProgressBar, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import subprocess
import os
from pathlib import Path
from ..utils import FileScanner, get_logger
from ..core import DocumentAnalyzer, IndexBuilder
from ..data import DatabaseManager
from .search_widget import SearchWidget

logger = get_logger(__name__)


class AnalysisWorker(QThread):
    progress = pyqtSignal(int)
    current_file = pyqtSignal(str)
    finished = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, documents, db, index_builder):
        super().__init__()
        self.documents = documents
        self.db = db
        self.index_builder = index_builder

    def run(self):
        try:
            total = len(self.documents)
            indexed_docs = []

            # Очищаем БД перед анализом
            self.db.clear_all()

            for i, doc_info in enumerate(self.documents):
                # Выводим название текущего файла
                file_name = Path(doc_info["file_path"]).name
                self.current_file.emit(f"Обработка: {file_name} ({i + 1}/{total})")

                # Анализируем документ
                doc = DocumentAnalyzer.analyze_file(
                    doc_info["file_path"],
                    doc_info.get("location"),
                    doc_info.get("year")
                )

                if doc:
                    # Сохраняем в БД
                    doc.id = self.db.add_document(doc)
                    indexed_docs.append(doc)

                progress_pct = int((i + 1) / total * 100)
                self.progress.emit(progress_pct)

            # Строим индекс
            self.index_builder.build_index(indexed_docs)
            self.finished.emit(len(indexed_docs))

        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Поисковик этнографического корпуса")
        self.setGeometry(100, 100, 1200, 800)

        # Компоненты
        self.scanner = FileScanner()
        self.documents = self.scanner.scan_documents()
        self.db = DatabaseManager()
        self.index_builder = IndexBuilder()

        # Основной виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Верхняя панель - одна строка (фиксированная высота)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        top_layout.setContentsMargins(5, 5, 5, 5)

        self.analyze_btn = QPushButton("Анализировать")
        self.analyze_btn.setMaximumWidth(120)
        self.analyze_btn.clicked.connect(self.on_analyze_clicked)
        top_layout.addWidget(self.analyze_btn)

        self.status_label = QLabel(f"Документов: {len(self.documents)}")
        top_layout.addWidget(self.status_label, 1)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setMaximumHeight(20)
        top_layout.addWidget(self.progress_bar)

        # Контейнер для верхней панели с фиксированной высотой
        top_widget = QWidget()
        top_widget.setLayout(top_layout)
        top_widget.setMaximumHeight(40)

        # Основное содержимое
        content_layout = QVBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.addWidget(top_widget)

        # Splitter для дерева и поиска
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Дерево документов
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Документы")
        self.tree.itemDoubleClicked.connect(self.on_tree_item_clicked)
        self.populate_tree()
        splitter.addWidget(self.tree)

        # Поиск
        self.search_widget = SearchWidget()
        self.search_widget.on_search_callback = self.perform_search
        self.search_widget.tree_widget = self.tree
        splitter.addWidget(self.search_widget)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        content_layout.addWidget(splitter)
        main_widget.setLayout(content_layout)

        self.analysis_worker = None
        logger.info(f"Loaded {len(self.documents)} documents")

    def populate_tree(self):
        """Заполняет дерево документов по году и месту"""
        years = {}
        for doc in self.documents:
            year = doc.get("year") or "Без года"
            location = doc.get("location") or "Без места"

            if year not in years:
                years[year] = {}
            if location not in years[year]:
                years[year][location] = []

            years[year][location].append(doc)

        for year in sorted(years.keys(), key=lambda x: (isinstance(x, str), -int(x) if isinstance(x, int) else 0), reverse=True):
            year_item = QTreeWidgetItem([f"{year}"])
            self.tree.addTopLevelItem(year_item)

            for location in sorted(years[year].keys()):
                location_item = QTreeWidgetItem([f"{location}"])
                year_item.addChild(location_item)

                for doc in years[year][location]:
                    doc_item = QTreeWidgetItem([doc["file_name"]])
                    doc_item.setData(0, Qt.ItemDataRole.UserRole, doc["file_path"])
                    location_item.addChild(doc_item)

    def on_analyze_clicked(self):
        """Анализирует все документы"""
        if self.analysis_worker and self.analysis_worker.isRunning():
            QMessageBox.warning(self, "Ошибка", "Анализ уже выполняется")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.analyze_btn.setEnabled(False)

        self.analysis_worker = AnalysisWorker(self.documents, self.db, self.index_builder)
        self.analysis_worker.progress.connect(self.on_progress)
        self.analysis_worker.current_file.connect(self.on_current_file)
        self.analysis_worker.finished.connect(self.on_analysis_finished)
        self.analysis_worker.error.connect(self.on_analysis_error)
        self.analysis_worker.start()

    def on_progress(self, value: int):
        """Обновляет прогресс-бар"""
        self.progress_bar.setValue(value)

    def on_current_file(self, file_info: str):
        """Обновляет информацию о текущем файле"""
        self.status_label.setText(file_info)

    def on_analysis_finished(self, count: int):
        """Завершение анализа"""
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        self.status_label.setText(f"✓ Документов: {count}")
        QMessageBox.information(self, "Успешно", f"Проиндексировано {count} документов")
        logger.info(f"Analysis completed: {count} documents indexed")

    def on_analysis_error(self, error: str):
        """Ошибка при анализе"""
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        QMessageBox.critical(self, "Ошибка", f"Ошибка при анализе: {error}")
        logger.error(f"Analysis error: {error}")

    def on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Открывает документ в Word при двойном клике"""
        file_path = item.data(0, Qt.ItemDataRole.UserRole)
        if file_path:
            full_path = Path(file_path)
            if full_path.exists():
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(str(full_path))
                    else:  # macOS / Linux
                        subprocess.Popen(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', str(full_path)])
                    logger.info(f"Opened in Word: {full_path.name}")
                except Exception as e:
                    logger.error(f"Could not open file: {e}")
                    QMessageBox.warning(self, "Ошибка", f"Не удалось открыть файл: {e}")
            else:
                QMessageBox.warning(self, "Ошибка", f"Файл не найден: {file_path}")
                logger.error(f"File not found: {file_path}")

    def perform_search(self, query: str):
        """Выполняет поиск"""
        from ..core import SearchEngine
        engine = SearchEngine()
        results = engine.search(query)
        self.search_widget.display_results(results)
