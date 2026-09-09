from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QStackedWidget,
)
from PySide6.QtCore import Qt

from app.ui.pages.record_page import RecordPage
from app.ui.pages.import_page import ImportPage
from app.ui.pages.settings_page import SettingsPage

from app.core.app_state import AppState


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "OfflineVoice"
        )

        self.resize(
            1100,
            720
        )

        self.setMinimumSize(
            900,
            600
        )

        self.current_page_index = 0

        self.setup_ui()

    def setup_ui(self):
        root = QWidget()

        self.setCentralWidget(
            root
        )

        main_layout = QHBoxLayout(
            root
        )

        main_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        main_layout.setSpacing(0)

        sidebar = QWidget()

        sidebar.setFixedWidth(
            190
        )

        sidebar_layout = QVBoxLayout(
            sidebar
        )

        sidebar_layout.setContentsMargins(
            12,
            20,
            12,
            12,
        )

        logo = QLabel(
            "OfflineVoice"
        )

        logo.setAlignment(
            Qt.AlignCenter
        )

        logo.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
            """
        )

        sidebar_layout.addWidget(
            logo
        )

        self.menu = QListWidget()

        self.menu.addItem(
            "🎤 录音转文字"
        )

        self.menu.addItem(
            "📂 音频转文字"
        )

        self.menu.addItem(
            "⚙ 设置"
        )

        self.menu.setStyleSheet(
            """
            QListWidget {
                border: none;
                font-size: 14px;
            }

            QListWidget::item {
                height: 42px;
                padding-left: 10px;
                border-radius: 6px;
            }

            QListWidget::item:selected {
                background: #dbeafe;
                color: #000000;
            }
            """
        )

        sidebar_layout.addWidget(
            self.menu
        )

        sidebar_layout.addStretch()

        version = QLabel(
            "OfflineVoice v1.0"
        )

        version.setAlignment(
            Qt.AlignCenter
        )

        version.setStyleSheet(
            """
            color: #888888;
            font-size: 11px;
            """
        )

        sidebar_layout.addWidget(
            version
        )

        content = QWidget()

        content_layout = QVBoxLayout(
            content
        )

        content_layout.setContentsMargins(
            15,
            15,
            15,
            15,
        )

        self.stack = QStackedWidget()

        self.record_page = RecordPage()

        self.import_page = ImportPage()

        self.settings_page = SettingsPage()

        self.stack.addWidget(
            self.record_page
        )

        self.stack.addWidget(
            self.import_page
        )

        self.stack.addWidget(
            self.settings_page
        )

        content_layout.addWidget(
            self.stack
        )

        main_layout.addWidget(
            sidebar
        )

        main_layout.addWidget(
            content,
            1
        )

        self.menu.currentRowChanged.connect(
            self.switch_page
        )

        self.menu.setCurrentRow(
            0
        )

    def switch_page(self, index):

        if AppState.busy():

            self.menu.blockSignals(True)

            self.menu.setCurrentRow(
                self.current_page_index
            )

            self.menu.blockSignals(False)

            return

        self.current_page_index = index

        self.stack.setCurrentIndex(index)


    def closeEvent(self, event):

        self.setEnabled(False)

        if hasattr(self, "record_page"):
            self.record_page.stop_worker()

        if hasattr(self, "import_page"):
            self.import_page.stop_worker()

        event.accept()