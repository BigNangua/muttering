import os
import wave
import threading

from datetime import datetime

import sounddevice as sd

from PySide6.QtCore import QObject, Signal

from app.recorder.segment import AudioSegment


class Recorder(QObject):

    segment_created = Signal(object)

    recording_started = Signal()

    recording_stopped = Signal()


    def __init__(
        self,
        interval_minutes=1
    ):
        super().__init__()

        self.sample_rate = 16000
        self.channels = 1

        self.interval_seconds = (
            interval_minutes * 60
        )

        self.record_dir = (
            "data/recordings"
        )

        os.makedirs(
            self.record_dir,
            exist_ok=True
        )

        self.running = False

        self.stream = None

        self.frames = []

        self.lock = threading.Lock()

        self.segment_index = 0

        self.record_thread = None


    # =====================
    # 开始录音
    # =====================

    def start(self):

        if self.running:
            return

        self.running = True

        self.frames = []

        self.segment_index = 0

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
            callback=self.callback
        )

        self.stream.start()

        self.record_thread = threading.Thread(
            target=self.segment_loop,
            daemon=True,
            name="RecorderSegmentThread"
        )

        self.record_thread.start()

        self.recording_started.emit()


    # =====================
    # 麦克风回调
    # =====================

    def callback(
        self,
        indata,
        frames,
        time,
        status
    ):

        if status:
            print(
                "录音状态:",
                status
            )

        if not self.running:
            return

        with self.lock:
            self.frames.append(
                indata.copy()
            )


    # =====================
    # 自动切片
    # =====================

    def segment_loop(self):
        print(
            "切片线程启动"
        )

        while self.running:
            print(
                "等待切片:",
                self.interval_seconds,
                "秒"
            )

            event = threading.Event()
            event.wait(
                self.interval_seconds
            )

            if not self.running:
                break
            print(
                "自动保存片段"
            )
            self.save_segment()
        print(
            "切片线程退出"
        )


    # =====================
    # 保存片段
    # =====================

    def save_segment(self):

        with self.lock:

            if not self.frames:
                return

            audio = b"".join(
                chunk.tobytes()
                for chunk in self.frames
            )

            self.frames = []


        filename = datetime.now().strftime(
            "%Y%m%d_%H%M%S.wav"
        )

        path = os.path.join(
            self.record_dir,
            filename
        )


        with wave.open(
            path,
            "wb"
        ) as wf:

            wf.setnchannels(
                self.channels
            )

            wf.setsampwidth(
                2
            )

            wf.setframerate(
                self.sample_rate
            )

            wf.writeframes(
                audio
            )


        self.segment_index += 1


        segment = AudioSegment(
            index=self.segment_index,
            path=path,
            start_time=datetime.now()
        )


        self.segment_created.emit(
            segment
        )


    # =====================
    # 停止录音
    # =====================

    def stop(self):

        if not self.running:
            return


        self.running = False


        if self.stream:

            self.stream.stop()

            self.stream.close()

            self.stream = None


        # 保存最后不足一个周期的数据

        self.save_segment()


        self.recording_stopped.emit()