import os
import queue
import threading
import wave

import numpy as np
import sounddevice as sd


class RecordingService:

    def __init__(
        self,
        sample_rate=16000,
        channels=1,
        chunk_seconds=60,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_seconds = chunk_seconds

        self.recording = False

        self.stream = None
        self.writer_thread = None

        self.audio_queue = queue.Queue()

        self.segment_lock = threading.Lock()
        self.segment_chunks = []

        self.output_file = None

        self.total_frames = 0
        self.segment_frames = 0

        self.writer_stop_event = threading.Event()

    def start(self, output_file):
        if self.recording:
            return

        output_dir = os.path.dirname(
            output_file
        )

        if output_dir:
            os.makedirs(
                output_dir,
                exist_ok=True
            )

        self.output_file = output_file

        self.recording = True

        self.total_frames = 0
        self.segment_frames = 0

        self.segment_chunks = []

        self.audio_queue = queue.Queue()

        self.writer_stop_event.clear()

        self.writer_thread = threading.Thread(
            target=self._writer_loop,
            daemon=True,
        )

        self.writer_thread.start()

        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
                callback=self._audio_callback,
            )

            self.stream.start()

        except Exception:
            self.recording = False
            self.writer_stop_event.set()

            if self.writer_thread:
                self.writer_thread.join(
                    timeout=2
                )

            self.writer_thread = None

            raise

    def _audio_callback(
        self,
        indata,
        frames,
        time_info,
        status,
    ):
        if status:
            print(
                "录音状态：",
                status
            )

        if not self.recording:
            return

        data = indata.copy()

        self.audio_queue.put(data)

    def _writer_loop(self):
        wav_file = None

        try:
            wav_file = wave.open(
                self.output_file,
                "wb"
            )

            wav_file.setnchannels(
                self.channels
            )

            wav_file.setsampwidth(2)

            wav_file.setframerate(
                self.sample_rate
            )

            while (
                self.recording
                or not self.audio_queue.empty()
                or not self.writer_stop_event.is_set()
            ):
                try:
                    data = self.audio_queue.get(
                        timeout=0.2
                    )
                except queue.Empty:
                    if self.writer_stop_event.is_set():
                        break

                    continue

                raw_data = data.tobytes()

                wav_file.writeframes(
                    raw_data
                )

                frames = len(data)

                self.total_frames += frames
                self.segment_frames += frames

                with self.segment_lock:
                    self.segment_chunks.append(
                        data
                    )

        finally:
            if wav_file:
                wav_file.close()

    def take_segment(self):
        with self.segment_lock:
            if not self.segment_chunks:
                return None

            chunks = self.segment_chunks

            self.segment_chunks = []

            self.segment_frames = 0

        if not chunks:
            return None

        return np.concatenate(
            chunks,
            axis=0
        )

    def stop(self):
        if not self.recording:
            return None

        self.recording = False

        if self.stream:
            try:
                self.stream.stop()
            except Exception:
                pass

            try:
                self.stream.close()
            except Exception:
                pass

            self.stream = None

        self.writer_stop_event.set()

        if self.writer_thread:
            self.writer_thread.join()

            self.writer_thread = None

        return self.take_segment()

    def get_duration(self):
        return (
            self.total_frames
            / self.sample_rate
        )

    def is_recording(self):
        return self.recording