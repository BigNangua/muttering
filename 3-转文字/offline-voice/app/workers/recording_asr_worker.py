from PySide6.QtCore import (
    QObject,
    Signal,
    Slot,
)

from app.asr.engine import ASREngine


class RecordingASRWorker(QObject):

    segment_result = Signal(
        int,
        str,
    )

    error = Signal(
        str
    )


    def __init__(self):

        super().__init__()

        self.engine = None


    def load_engine(self):

        if self.engine is None:

            self.engine = ASREngine(
                model_size="medium",
                device="cpu",
                compute_type="int8",
            )


    @Slot(str, int)
    def transcribe_segment(
        self,
        audio_file,
        segment_index,
    ):

        try:

            self.load_engine()


            result = self.engine.transcribe(
                audio_file
            )


            text = result.get(
                "text",
                ""
            )


            self.segment_result.emit(
                segment_index,
                text,
            )


        except Exception as e:

            self.error.emit(
                f"第 {segment_index} 段识别失败：{e}"
            )