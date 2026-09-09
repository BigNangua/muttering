from enum import Enum


class AppStatus(Enum):
    IDLE = "idle"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"


class AppState:
    status = AppStatus.IDLE

    @classmethod
    def busy(cls):
        return cls.status != AppStatus.IDLE

    @classmethod
    def set_status(cls, status):
        cls.status = status

    @classmethod
    def reset(cls):
        cls.status = AppStatus.IDLE