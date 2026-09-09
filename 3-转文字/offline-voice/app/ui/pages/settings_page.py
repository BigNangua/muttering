from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QLabel,
    QGroupBox,
)

from app.config.settings import (
    get_available_models,
    load_settings,
    save_settings,
)


class SettingsPage(QWidget):
    """
    OfflineVoice 设置页面。
    """

    settings_changed = Signal()

    def __init__(self):
        super().__init__()

        self.settings = load_settings()

        self.init_ui()
        self.load_ui_values()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        main_layout.setContentsMargins(
            30,
            30,
            30,
            30,
        )

        main_layout.setSpacing(20)

        # =========================
        # 识别设置
        # =========================

        asr_group = QGroupBox("识别设置")

        asr_layout = QFormLayout()

        asr_layout.setLabelAlignment(
            Qt.AlignLeft
        )

        self.model_combo = QComboBox()

        self.model_combo.setMinimumWidth(240)

        asr_layout.addRow(
            "识别模型",
            self.model_combo,
        )

        asr_group.setLayout(asr_layout)

        main_layout.addWidget(asr_group)

        # =========================
        # 录音设置
        # =========================

        recording_group = QGroupBox("录音设置")

        recording_layout = QFormLayout()

        self.segment_combo = QComboBox()

        self.segment_combo.setMinimumWidth(240)

        self.segment_combo.addItem(
            "1 分钟",
            60,
        )

        self.segment_combo.addItem(
            "2 分钟",
            120,
        )

        self.segment_combo.addItem(
            "3 分钟",
            180,
        )

        self.segment_combo.addItem(
            "5 分钟",
            300,
        )

        recording_layout.addRow(
            "自动转写间隔",
            self.segment_combo,
        )

        recording_group.setLayout(
            recording_layout
        )

        main_layout.addWidget(
            recording_group
        )

        # =========================
        # 音频参数
        # =========================

        audio_group = QGroupBox("录音参数")

        audio_layout = QFormLayout()

        sample_rate_label = QLabel(
            "16000 Hz"
        )

        channels_label = QLabel(
            "单声道"
        )

        audio_layout.addRow(
            "采样率",
            sample_rate_label,
        )

        audio_layout.addRow(
            "声道",
            channels_label,
        )

        audio_group.setLayout(
            audio_layout
        )

        main_layout.addWidget(
            audio_group
        )

        # =========================
        # 说明
        # =========================

        self.model_info_label = QLabel()

        self.model_info_label.setWordWrap(
            True
        )

        main_layout.addWidget(
            self.model_info_label
        )

        main_layout.addStretch()

        # 设置变化后立即保存
        self.model_combo.currentIndexChanged.connect(
            self.on_settings_changed
        )

        self.segment_combo.currentIndexChanged.connect(
            self.on_settings_changed
        )

    def load_ui_values(self):
        """
        加载模型列表和当前设置。
        """

        # =========================
        # 加载模型
        # =========================

        self.model_combo.blockSignals(True)

        self.model_combo.clear()

        models = get_available_models()

        current_model = self.settings.get(
            "model_size",
            "medium",
        )

        if not models:
            self.model_combo.addItem(
                "没有发现本地模型",
                None,
            )

            self.model_info_label.setText(
                "请将 faster-whisper 模型放入：\n"
                "models/whisper/"
            )

        else:
            for model in models:
                self.model_combo.addItem(
                    model,
                    model,
                )

            index = self.model_combo.findData(
                current_model
            )

            if index >= 0:
                self.model_combo.setCurrentIndex(
                    index
                )
            else:
                self.model_combo.setCurrentIndex(0)

                # 如果原来的模型不存在，
                # 自动使用第一个可用模型
                self.settings["model_size"] = (
                    self.model_combo.currentData()
                )

            self.model_info_label.setText(
                f"已发现 {len(models)} 个本地模型\n"
                f"模型目录：models/whisper/"
            )

        self.model_combo.blockSignals(False)

        # =========================
        # 自动转写间隔
        # =========================

        self.segment_combo.blockSignals(True)

        segment_seconds = int(
            self.settings.get(
                "segment_seconds",
                60,
            )
        )

        index = self.segment_combo.findData(
            segment_seconds
        )

        if index >= 0:
            self.segment_combo.setCurrentIndex(
                index
            )
        else:
            self.segment_combo.setCurrentIndex(0)

            self.settings[
                "segment_seconds"
            ] = 60

        self.segment_combo.blockSignals(False)

    def on_settings_changed(self):
        """
        保存设置。
        """

        model = self.model_combo.currentData()

        if model is None:
            return

        segment_seconds = (
            self.segment_combo.currentData()
        )

        self.settings["model_size"] = model

        self.settings[
            "segment_seconds"
        ] = segment_seconds

        save_settings(self.settings)

        self.settings_changed.emit()

    def refresh_models(self):
        """
        重新扫描模型目录。
        """

        old_model = self.model_combo.currentData()

        self.settings = load_settings()

        self.model_combo.blockSignals(True)

        self.model_combo.clear()

        models = get_available_models()

        if not models:
            self.model_combo.addItem(
                "没有发现本地模型",
                None,
            )

            self.model_info_label.setText(
                "请将模型放入：models/whisper/"
            )

        else:
            for model in models:
                self.model_combo.addItem(
                    model,
                    model,
                )

            index = self.model_combo.findData(
                old_model
            )

            if index < 0:
                index = self.model_combo.findData(
                    self.settings.get(
                        "model_size",
                        "medium",
                    )
                )

            if index < 0:
                index = 0

            self.model_combo.setCurrentIndex(
                index
            )

            self.model_info_label.setText(
                f"已发现 {len(models)} 个本地模型\n"
                f"模型目录：models/whisper/"
            )

        self.model_combo.blockSignals(False)

        self.on_settings_changed()