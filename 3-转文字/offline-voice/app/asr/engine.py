import os
import time
from pathlib import Path

import psutil
from faster_whisper import WhisperModel


class ASREngine:
    """
    OfflineVoice 本地 Whisper ASR 引擎。

    模型直接从项目的 models/whisper/ 下加载，
    不依赖 Hugging Face 在线下载。
    """

    def __init__(
        self,
        model_size="medium",
        device="cpu",
        compute_type="int8",
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type

        self.model = None

        # 项目根目录
        self.base_dir = Path(__file__).resolve().parents[2]

        # 本地模型目录
        self.model_dir = (
            self.base_dir
            / "models"
            / "whisper"
            / self.model_size
        )

    def load_model(self):
        """
        加载本地模型。
        """

        if self.model is not None:
            return

        if not self.model_dir.exists():
            raise FileNotFoundError(
                f"本地模型不存在：{self.model_dir}"
            )

        config_file = self.model_dir / "config.json"
        model_file = self.model_dir / "model.bin"

        if not config_file.exists():
            raise FileNotFoundError(
                f"模型缺少 config.json：{self.model_dir}"
            )

        if not model_file.exists():
            raise FileNotFoundError(
                f"模型缺少 model.bin：{self.model_dir}"
            )

        print(f"正在加载本地模型：{self.model_dir}")

        self.model = WhisperModel(
            str(self.model_dir),
            device=self.device,
            compute_type=self.compute_type,
        )

        print("本地模型加载成功")

    def transcribe(
        self,
        audio_file,
        language="zh",
        beam_size=5,
    ):
        """
        识别音频。
        """

        self.load_model()

        process = psutil.Process(os.getpid())

        start_time = time.perf_counter()

        segments, info = self.model.transcribe(
            audio_file,
            language=language,
            beam_size=beam_size,
            vad_filter=True,
        )

        texts = []

        for segment in segments:
            text = segment.text.strip()

            if text:
                texts.append(text)

        text = "".join(texts)

        recognize_time = (
            time.perf_counter() - start_time
        )

        audio_duration = (
            info.duration
            if info.duration
            else 0
        )

        speed = (
            audio_duration / recognize_time
            if recognize_time > 0
            else 0
        )

        memory = (
            process.memory_info().rss
            / 1024
            / 1024
        )

        return {
            "text": text,
            "model": self.model_size,
            "device": self.device,
            "compute_type": self.compute_type,
            "language": info.language,
            "audio_duration": audio_duration,
            "recognize_time": recognize_time,
            "speed": speed,
            "memory": memory,
        }