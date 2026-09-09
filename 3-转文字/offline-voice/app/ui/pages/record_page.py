import os
import wave
from datetime import datetime

import soundfile as sf

from PySide6.QtCore import (
    QTimer,
    QThread,
    Signal,
    Qt,
)

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
)

from app.audio.recording_service import (
    RecordingService,
)

from app.config.settings import (
    load_settings,
    SAMPLE_RATE,
    CHANNELS,
)

from app.storage.recording_storage import (
    create_recording_session,
    save_transcript,
    save_markdown,
)

from app.workers.recording_asr_worker import (
    RecordingASRWorker,
)

from app.core.app_state import (
    AppState,
    AppStatus,
)


class RecordPage(QWidget):

    segment_requested = Signal(
        str,
        int,
    )

    def __init__(self):
        super().__init__()

        # 先读取最新设置
        settings = load_settings()

        self.segment_seconds = int(
            settings.get(
                "segment_seconds",
                60,
            )
        )

        self.sample_rate = int(
            settings.get(
                "sample_rate",
                16000,
            )
        )

        self.channels = int(
            settings.get(
                "channels",
                1,
            )
        )

        self.recording_service = RecordingService(
            sample_rate=self.sample_rate,
            channels=self.channels,
            chunk_seconds=self.segment_seconds,
        )

        self.recording_thread = None
        self.recording_worker = None

        self.session = None

        self.recording = False

        self.record_seconds = 0

        self.segment_index = 0

        self.transcript_parts = {}

        self.pending_segments = {}

        self.next_segment_to_send = 0

        self.setup_ui()

        self.setup_timer()

        self.setup_asr_worker()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            10,
            10,
            10,
            10,
        )

        layout.setSpacing(10)

        title = QLabel(
            "录音转文字"
        )

        title.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
            """
        )

        layout.addWidget(
            title
        )

        self.time_label = QLabel(
            "00:00"
        )

        self.time_label.setStyleSheet(
            """
            font-size: 32px;
            font-weight: bold;
            """
        )

        self.time_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            self.time_label
        )

        self.status_label = QLabel(
            "状态：等待录音"
        )

        self.status_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            self.status_label
        )

        button_layout = QHBoxLayout()

        self.start_button = QPushButton(
            "开始录音"
        )

        self.start_button.setMinimumHeight(
            42
        )

        self.stop_button = QPushButton(
            "停止并完成"
        )

        self.stop_button.setMinimumHeight(
            42
        )

        self.stop_button.setEnabled(
            False
        )

        button_layout.addWidget(
            self.start_button
        )

        button_layout.addWidget(
            self.stop_button
        )

        layout.addLayout(
            button_layout
        )

        self.progress_label = QLabel(
            f"自动转写：每 {self.segment_seconds // 60} 分钟一次"
        )

        self.progress_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            self.progress_label
        )

        result_title = QLabel(
            "识别结果"
        )

        result_title.setStyleSheet(
            """
            font-size: 16px;
            font-weight: bold;
            """
        )

        layout.addWidget(
            result_title
        )

        from PySide6.QtWidgets import QTextEdit

        self.result_text = QTextEdit()

        self.result_text.setReadOnly(
            True
        )

        self.result_text.setPlaceholderText(
            "开始录音后，识别文字会显示在这里"
        )

        layout.addWidget(
            self.result_text,
            1
        )

        action_layout = QHBoxLayout()

        self.open_button = QPushButton(
            "打开录音目录"
        )

        self.open_button.setEnabled(
            False
        )

        self.copy_button = QPushButton(
            "复制文字"
        )

        self.copy_button.setEnabled(
            False
        )

        action_layout.addWidget(
            self.open_button
        )

        action_layout.addWidget(
            self.copy_button
        )

        layout.addLayout(
            action_layout
        )

        self.start_button.clicked.connect(
            self.start_recording
        )

        self.stop_button.clicked.connect(
            self.stop_recording
        )

        self.open_button.clicked.connect(
            self.open_recording_directory
        )

        self.copy_button.clicked.connect(
            self.copy_text
        )

    def setup_timer(self):
        self.record_timer = QTimer(
            self
        )

        self.record_timer.setInterval(
            1000
        )

        self.record_timer.timeout.connect(
            self.update_time
        )

        self.segment_timer = QTimer(
            self
        )

        self.segment_timer.setInterval(
            self.segment_seconds * 1000
        )

        self.segment_timer.timeout.connect(
            self.process_segment
        )

    def setup_asr_worker(self):
        self.recording_thread = QThread(
            self
        )

        self.recording_worker = (
            RecordingASRWorker()
        )

        self.recording_worker.moveToThread(
            self.recording_thread
        )

        self.segment_requested.connect(
            self.recording_worker.transcribe_segment,
            Qt.QueuedConnection,
        )

        self.recording_worker.segment_result.connect(
            self.on_segment_result
        )

        self.recording_worker.error.connect(
            self.on_asr_error
        )

        self.recording_thread.start()

    def start_recording(self):

        if self.recording:
            return

        if AppState.busy():
            return

        AppState.set_status(
            AppStatus.RECORDING
        )

        # 重新读取用户设置
        settings = load_settings()

        self.segment_seconds = int(
            settings.get(
                "segment_seconds",
                60
            )
        )

        # 更新切片时间
        self.segment_timer.setInterval(
            self.segment_seconds * 1000
        )


        # 重新创建录音服务
        self.recording_service = RecordingService(
            sample_rate=SAMPLE_RATE,
            channels=CHANNELS,
            chunk_seconds=self.segment_seconds,
        )


        self.session = (
            create_recording_session()
        )

        self.recording_service.start(
            self.session["audio"]
        )

        self.recording = True

        self.record_seconds = 0

        self.segment_index = 0

        self.transcript_parts = {}

        self.pending_segments = {}

        self.next_segment_to_send = 0

        self.result_text.clear()

        self.time_label.setText(
            "00:00"
        )

        self.status_label.setText(
            "状态：正在录音"
        )

        self.progress_label.setText(
            f"自动转写：等待 {self.segment_seconds // 60} 分钟"
        )

        self.start_button.setEnabled(
            False
        )

        self.stop_button.setEnabled(
            True
        )

        self.open_button.setEnabled(
            False
        )

        self.copy_button.setEnabled(
            False
        )

        self.record_timer.start()

        self.segment_timer.start()


    def update_time(self):
        if not self.recording:
            return

        self.record_seconds += 1

        minutes = (
            self.record_seconds // 60
        )

        seconds = (
            self.record_seconds % 60
        )

        self.time_label.setText(
            f"{minutes:02d}:{seconds:02d}"
        )

    def process_segment(self):
        if not self.recording:
            return

        AppState.set_status(
            AppStatus.TRANSCRIBING
        )

        audio = (
            self.recording_service.take_segment()
        )

        if audio is None:
            return

        self.segment_index += 1

        segment_index = self.segment_index

        segment_file = self.create_segment_file(
            audio,
            segment_index,
        )

        if not segment_file:
            return

        self.pending_segments[
            segment_index
        ] = segment_file

        self.segment_requested.emit(
            segment_file,
            segment_index,
        )

        self.progress_label.setText(
            f"自动转写：第 {segment_index} 段识别中"
        )

    def create_segment_file(
        self,
        audio,
        segment_index,
    ):
        try:
            segment_dir = os.path.join(
                self.session["directory"],
                "segments",
            )

            os.makedirs(
                segment_dir,
                exist_ok=True
            )

            path = os.path.join(
                segment_dir,
                f"segment_{segment_index:04d}.wav",
            )

            sf.write(
                path,
                audio,
                SAMPLE_RATE,
                subtype="PCM_16",
            )

            return path

        except Exception as e:
            QMessageBox.critical(
                self,
                "保存分段失败",
                str(e),
            )

            return None

    def on_segment_result(
        self,
        segment_index,
        text,
    ):
        self.transcript_parts[
            segment_index
        ] = text

        AppState.set_status(
            AppStatus.RECORDING
        )

        self.update_transcript_display()

        self.progress_label.setText(
            f"自动转写：第 {segment_index} 段完成"
        )

        self.save_current_transcript()

    def update_transcript_display(self):
        parts = []

        for index in sorted(
            self.transcript_parts
        ):
            text = self.transcript_parts[
                index
            ]

            if text:
                parts.append(
                    text
                )

        self.result_text.setPlainText(
            "\n".join(parts)
        )

        scrollbar = (
            self.result_text.verticalScrollBar()
        )

        scrollbar.setValue(
            scrollbar.maximum()
        )

        self.copy_button.setEnabled(
            bool(parts)
        )

    def save_current_transcript(self):
        if not self.session:
            return

        text = self.result_text.toPlainText()

        save_transcript(
            self.session["text"],
            text,
        )

    def stop_recording(self):
        if not self.recording:
            return

        self.status_label.setText(
            "状态：正在完成最后一次转写..."
        )

        self.start_button.setEnabled(
            False
        )

        self.stop_button.setEnabled(
            False
        )

        self.record_timer.stop()

        self.segment_timer.stop()

        self.recording = False

        last_audio = (
            self.recording_service.stop()
        )

        if last_audio is not None:
            self.segment_index += 1

            segment_index = (
                self.segment_index
            )

            segment_file = (
                self.create_segment_file(
                    last_audio,
                    segment_index,
                )
            )

            if segment_file:
                self.pending_segments[
                    segment_index
                ] = segment_file

                self.segment_requested.emit(
                    segment_file,
                    segment_index,
                )

        self.finish_when_ready()

    def finish_when_ready(self):
        expected = set(
            self.pending_segments.keys()
        )

        finished = set(
            self.transcript_parts.keys()
        )

        if expected.issubset(finished):
            self.finish_recording()

            return

        QTimer.singleShot(
            500,
            self.finish_when_ready,
        )

    def finish_recording(self):
        text = self.result_text.toPlainText()

        save_transcript(
            self.session["text"],
            text,
        )

        save_markdown(
            self.session["markdown"],
            text,
        )

        self.status_label.setText(
            "状态：录音完成"
        )

        self.progress_label.setText(
            "录音、文字已保存"
        )

        self.start_button.setEnabled(
            True
        )

        self.stop_button.setEnabled(
            False
        )

        self.open_button.setEnabled(
            True
        )

        self.copy_button.setEnabled(
            bool(text)
        )
        AppState.reset()


    def on_asr_error(
        self,
        message,
    ):

        AppState.reset()
        
        self.status_label.setText(
            "状态：部分识别失败"
        )

        QMessageBox.warning(
            self,
            "识别失败",
            message,
        )

    def open_recording_directory(self):
        if not self.session:
            return

        path = os.path.abspath(
            self.session["directory"]
        )

        if os.name == "nt":
            os.startfile(path)

    def copy_text(self):
        text = self.result_text.toPlainText()

        if not text:
            return

        from PySide6.QtWidgets import QApplication

        QApplication.clipboard().setText(
            text
        )

    def stop_worker(self):
        if self.recording:
            self.stop_recording()

        if self.recording_thread:
            self.recording_thread.quit()

            self.recording_thread.wait()

            self.recording_thread = None