from PySide6.QtCore import QThread, Signal

from app.asr.engine import ASREngine
from app.config.settings import load_settings


class ASRWorker(QThread):
    result_ready = Signal(dict)
    error = Signal(str)

    def __init__(self, audio_file):
        super().__init__()
        self.audio_file = audio_file
        self._stop_requested = False

    def run(self):
        try:
            settings = load_settings()
            model_size = settings.get("model_size", "medium")
            language = settings.get("language", "zh")

            engine = ASREngine(
                model_size=model_size,
                device="cpu",
                compute_type="int8",
            )

            if self._stop_requested:
                return

            result = engine.transcribe(
                self.audio_file,
                language=language,
            )

            if self._stop_requested:
                return

            self.result_ready.emit(result)

        except Exception as e:
            if not self._stop_requested:
                self.error.emit(str(e))

    def stop(self):
        self._stop_requested = True