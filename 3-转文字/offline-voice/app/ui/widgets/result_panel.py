from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QApplication,
    QHBoxLayout,
)


class ResultPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(8)

        self.result_text = QTextEdit()

        self.result_text.setReadOnly(
            True
        )

        self.result_text.setPlaceholderText(
            "识别结果会显示在这里"
        )

        self.result_text.setStyleSheet(
            """
            QTextEdit {
                font-size: 15px;
                padding: 8px;
            }
            """
        )

        layout.addWidget(
            self.result_text
        )

        button_layout = QHBoxLayout()

        button_layout.setSpacing(8)

        self.copy_button = QPushButton(
            "复制"
        )

        self.copy_button.clicked.connect(
            self.copy_text
        )

        self.txt_button = QPushButton(
            "导出 TXT"
        )

        self.md_button = QPushButton(
            "导出 Markdown"
        )

        self.copy_button.setEnabled(
            False
        )

        self.txt_button.setEnabled(
            False
        )

        self.md_button.setEnabled(
            False
        )

        button_layout.addWidget(
            self.copy_button
        )

        button_layout.addWidget(
            self.txt_button
        )

        button_layout.addWidget(
            self.md_button
        )

        layout.addLayout(
            button_layout
        )

    def set_text(
        self,
        text,
    ):
        self.result_text.setPlainText(
            text
        )

    def get_text(self):
        return self.result_text.toPlainText()

    def enable_actions(self):
        self.copy_button.setEnabled(
            True
        )

        self.txt_button.setEnabled(
            True
        )

        self.md_button.setEnabled(
            True
        )

    def clear(self):
        self.result_text.clear()

        self.copy_button.setEnabled(
            False
        )

        self.txt_button.setEnabled(
            False
        )

        self.md_button.setEnabled(
            False
        )

    def copy_text(self):
        text = self.get_text()

        if not text:
            return

        QApplication.clipboard().setText(
            text
        )