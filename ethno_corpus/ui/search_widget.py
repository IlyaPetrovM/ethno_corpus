from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QLabel
from PyQt5.QtCore import Qt
from ..utils import get_logger

logger = get_logger(__name__)


class SearchWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.on_search_callback = None
        self.tree_widget = None
        self.last_expanded_path = None

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
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.on_result_clicked)

        layout.addLayout(search_layout)
        layout.addWidget(self.results_count_label)
        layout.addWidget(self.results_list)

        self.setLayout(layout)

    def on_search_clicked(self):
        """Обработчик нажатия кнопки 'Искать'"""
        query = self.search_input.text().strip()
        if not query or not self.on_search_callback:
            return

        logger.info(f"Search query: {query}")
        self.on_search_callback(query)

    def display_results(self, results: list):
        """Отображает результаты поиска"""
        self.results_list.clear()
        self.results_count_label.setText(f"Результатов: {len(results)}")

        for i, result in enumerate(results):
            # Форматируем результат для отображения
            context = result.get("context", "")[:100] + "..."

            item = QListWidgetItem(context)
            item.setData(Qt.ItemDataRole.UserRole, result)
            self.results_list.addItem(item)

    def on_result_clicked(self, item: QListWidgetItem):
        """Обработчик клика на результат поиска - открывает документ в дереве"""
        if not self.tree_widget:
            return

        result = item.data(Qt.ItemDataRole.UserRole)
        if result:
            file_path = result.get("file_path")
            if file_path:
                self.navigate_tree_to_document(file_path)

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
