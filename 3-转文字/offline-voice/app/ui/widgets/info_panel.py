from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QFrame,
)


class InfoPanel(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(24)

        self.model_label = self.create_item(
            "模型",
            "-"
        )

        self.device_label = self.create_item(
            "设备",
            "-"
        )

        self.language_label = self.create_item(
            "语言",
            "-"
        )

        self.duration_label = self.create_item(
            "音频长度",
            "-"
        )

        self.speed_label = self.create_item(
            "速度",
            "-"
        )

        for widget in (
            self.model_label,
            self.device_label,
            self.language_label,
            self.duration_label,
            self.speed_label,
        ):
            layout.addWidget(widget)

        layout.addStretch()

    def create_item(
        self,
        title,
        value,
    ):
        frame = QFrame()

        layout = QHBoxLayout(frame)

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(5)

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet(
            """
            color: #777777;
            font-size: 12px;
            """
        )

        value_label = QLabel(
            value
        )

        value_label.setStyleSheet(
            """
            font-size: 13px;
            font-weight: bold;
            """
        )

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            value_label
        )

        frame.value_label = value_label

        return frame

    def update_info(
        self,
        result,
    ):
        duration = result.get(
            "audio_duration",
            0
        )

        minutes = int(
            duration // 60
        )

        seconds = int(
            duration % 60
        )

        self.model_label.value_label.setText(
            result.get("model", "-")
        )

        self.device_label.value_label.setText(
            result.get("device", "-")
        )

        self.language_label.value_label.setText(
            result.get("language", "-")
        )

        self.duration_label.value_label.setText(
            f"{minutes:02d}:{seconds:02d}"
        )

        self.speed_label.value_label.setText(
            f'{result.get("speed", 0):.2f}x'
        )