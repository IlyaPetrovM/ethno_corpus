from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextBrowser, QLabel
from PyQt5.QtCore import Qt, QUrl
from hsluv import hpluv_to_rgb
import random
from ..utils import get_logger

logger = get_logger(__name__)


class SearchWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.on_search_callback = None
        self.tree_widget = None
        self.last_expanded_path = None
        self.search_results = []

        layout = QVBoxLayout()

        # Строка поиска
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст для поиска...")
        self.search_input.returnPressed.connect(self.on_search_clicked)
        self.search_btn = QPushButton("Искать")
        self.search_btn.clicked.connect(self.on_search_clicked)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_btn)

        # Результаты поиска
        self.results_count_label = QLabel("Результатов: 0")
        self.results_browser = QTextBrowser()
        self.results_browser.setOpenLinks(False)
        self.results_browser.anchorClicked.connect(self.on_result_clicked)

        layout.addLayout(search_layout)
        layout.addWidget(self.results_count_label)
        layout.addWidget(self.results_browser)

        self.setLayout(layout)

    def on_search_clicked(self):
        """Обработчик нажатия кнопки 'Искать'"""
        query = self.search_input.text().strip()
        if not query or not self.on_search_callback:
            return

        logger.info(f"Search query: {query}")
        self.on_search_callback(query)

    @staticmethod
    def _file_color(file_path: str, color_cache: dict) -> str:
        """Возвращает HEX цвет для файла: одинаковый для одного файла, разный для разных"""
        if file_path not in color_cache:
            hue = random.uniform(0, 360)
            r, g, b = hpluv_to_rgb([hue, 100, 95])
            color_cache[file_path] = "#{:02x}{:02x}{:02x}".format(
                int(r * 255), int(g * 255), int(b * 255)
            )
        return color_cache[file_path]

    def display_results(self, results: list):
        """Отображает результаты поиска с подсветкой найденных слов"""
        self.results_browser.clear()
        self.results_count_label.setText(f"Результатов: {len(results)}")
        self.search_results = results

        color_cache = {}
        html_content = '<div style="font-family: Arial; font-size: 10pt;">'

        for i, result in enumerate(results):
            context = result.get("context", "")
            file_path = result.get("file_path", "")
            bg_color = self._file_color(file_path, color_cache)

            html_content += f'<div style="margin-bottom: 4px; padding: 6px; background-color: {bg_color};">'
            html_content += f'<a href="result_{i}" style="color: #333; text-decoration: none; line-height: 1.5;">{context}</a>'
            html_content += '</div>'

        html_content += '</div>'
        self.results_browser.setHtml(html_content)

    def on_result_clicked(self, url: QUrl):
        """Обработчик клика на результат поиска - открывает документ в дереве"""
        if not self.tree_widget:
            return

        # Парсим номер результата из URL
        anchor = url.toString()
        if anchor.startswith("result_"):
            try:
                result_idx = int(anchor.split("_")[1])
                if 0 <= result_idx < len(self.search_results):
                    result = self.search_results[result_idx]
                    file_path = result.get("file_path")
                    if file_path:
                        self.navigate_tree_to_document(file_path)
            except (ValueError, IndexError):
                pass

    def navigate_tree_to_document(self, file_path):
        """Открывает документ в дереве: закрывает предыдущую ветку, раскрывает новую"""
        if not self.tree_widget:
            return

        root = self.tree_widget.invisibleRootItem()

        # Закрываем предыдущую открытую ветку
        if self.last_expanded_path:
            for item in self.last_expanded_path:
                self.tree_widget.collapseItem(item)

        # Поиск документа в дереве по file_path
        def search_and_expand(parent_item):
            for i in range(parent_item.childCount()):
                child = parent_item.child(i)
                stored_path = child.data(0, Qt.ItemDataRole.UserRole)

                if stored_path == file_path:
                    # Нашли документ - раскрываем все родительские узлы и сохраняем путь
                    expanded_items = []
                    current = child
                    while current:
                        parent = current.parent()
                        if parent and parent != root:
                            self.tree_widget.expandItem(parent)
                            expanded_items.append(parent)
                        current = parent

                    self.last_expanded_path = expanded_items
                    # Выбираем документ
                    self.tree_widget.setCurrentItem(child)
                    self.tree_widget.scrollToItem(child)
                    return True

                # Рекурсивно ищем в потомках
                if search_and_expand(child):
                    return True

            return False

        search_and_expand(root)
