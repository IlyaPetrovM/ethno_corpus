from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel
from PyQt5.QtCore import Qt


class TextViewerWindow(QMainWindow):
    def __init__(self, file_name: str, content: str, passport: str = "", highlighted_words: list = None):
        super().__init__()
        self.setWindowTitle(f"Просмотр: {file_name}")
        self.setGeometry(200, 200, 800, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout()

        # Паспорт интервью
        if passport:
            passport_label = QLabel("Паспорт интервью:")
            passport_text = QTextEdit()
            passport_text.setText(passport)
            passport_text.setReadOnly(True)
            passport_text.setMaximumHeight(80)
            layout.addWidget(passport_label)
            layout.addWidget(passport_text)

        # Содержимое
        content_label = QLabel("Содержание:")
        self.text_edit = QTextEdit()
        self.text_edit.setText(content)
        self.text_edit.setReadOnly(True)

        layout.addWidget(content_label)
        layout.addWidget(self.text_edit)

        main_widget.setLayout(layout)
