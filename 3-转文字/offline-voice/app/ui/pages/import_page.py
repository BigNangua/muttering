import os

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
)

from app.workers.asr_worker import ASRWorker
from app.ui.widgets.result_panel import ResultPanel
from app.ui.widgets.info_panel import InfoPanel
from app.export.exporter import export_txt, export_markdown

from app.core.app_state import (
    AppState,
    AppStatus,
)

class ImportPage(QWidget):
    def __init__(self):
        super().__init__()
        self.audio_file = None
        self.worker = None
        self.current_result = None
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel("音频转文字")
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
        """)
        layout.addWidget(title)

        self.select_button = QPushButton("选择音频")
        self.select_button.setMinimumHeight(38)
        layout.addWidget(self.select_button)

        self.file_label = QLabel("尚未选择音频")
        self.file_label.setWordWrap(True)
        layout.addWidget(self.file_label)

        self.transcribe_button = QPushButton("开始识别")
        self.transcribe_button.setMinimumHeight(38)
        self.transcribe_button.setEnabled(False)
        layout.addWidget(self.transcribe_button)

        self.status_label = QLabel("状态：等待操作")
        layout.addWidget(self.status_label)

        self.info_panel = InfoPanel()
        layout.addWidget(self.info_panel)

        self.result_panel = ResultPanel()
        layout.addWidget(self.result_panel, 1)

    def connect_signals(self):
        self.select_button.clicked.connect(self.select_audio)
        self.transcribe_button.clicked.connect(self.start_transcription)
        self.result_panel.txt_button.clicked.connect(self.export_txt_file)
        self.result_panel.md_button.clicked.connect(self.export_md_file)

    def select_audio(self):
        if self.worker is not None and self.worker.isRunning():
            return

        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择音频",
            "",
            "Audio Files (*.wav *.mp3 *.m4a *.flac *.aac *.ogg *.wma)",
        )

        if not path:
            return

        self.audio_file = path
        filename = os.path.basename(path)

        self.file_label.setText(
            f"已选择：{filename}\n{path}"
        )

        self.transcribe_button.setEnabled(True)
        self.status_label.setText("状态：已选择音频")
        self.result_panel.clear()
        self.current_result = None

    def start_transcription(self):

        if not self.audio_file:
            return

        if AppState.busy():
            return

        AppState.set_status(
            AppStatus.TRANSCRIBING
        )

        self.select_button.setEnabled(
            False
        )

        self.transcribe_button.setEnabled(
            False
        )

        self.status_label.setText(
            "状态：正在识别..."
        )

        self.worker = ASRWorker(
            self.audio_file
        )

        self.worker.result_ready.connect(
            self.on_result
        )

        self.worker.error.connect(
            self.on_error
        )

        self.worker.finished.connect(
            self.on_worker_finished
        )

        self.worker.start()

    def on_result(self, result):

        AppState.reset()

        self.current_result = result

        self.result_panel.set_text(
            result.get("text", "")
        )

        self.result_panel.enable_actions()

        self.info_panel.update_info(result)

        self.status_label.setText("状态：识别完成")

    def on_error(self, message):

        AppState.reset()

        self.status_label.setText("状态：识别失败")

        self.select_button.setEnabled(True)
        self.transcribe_button.setEnabled(
            self.audio_file is not None
        )

        QMessageBox.critical(
            self,
            "识别失败",
            message,
        )

    def on_worker_finished(self):

        worker = self.worker

        self.worker = None

        if worker is not None:
            worker.deleteLater()

        self.select_button.setEnabled(
            True
        )

        self.transcribe_button.setEnabled(
            self.audio_file is not None
        )

        if self.current_result:
            self.status_label.setText(
                "状态：识别完成"
            )

    def export_txt_file(self):
        if not self.current_result:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "保存 TXT",
            "transcript.txt",
            "Text Files (*.txt)",
        )

        if not path:
            return

        try:
            export_txt(
                path,
                self.current_result,
            )

            QMessageBox.information(
                self,
                "导出成功",
                "TXT 已保存。",
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "导出失败",
                str(e),
            )

    def export_md_file(self):
        if not self.current_result:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            "保存 Markdown",
            "transcript.md",
            "Markdown Files (*.md)",
        )

        if not path:
            return

        try:
            export_markdown(
                path,
                self.current_result,
            )

            QMessageBox.information(
                self,
                "导出成功",
                "Markdown 已保存。",
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "导出失败",
                str(e),
            )

    def stop_worker(self):

        worker = self.worker

        self.worker = None

        if worker is None:
            AppState.reset()
            return

        if worker.isRunning():
            worker.wait()

        worker.deleteLater()

        AppState.reset()