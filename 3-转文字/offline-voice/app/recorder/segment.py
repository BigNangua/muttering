from dataclasses import dataclass
from datetime import datetime


@dataclass
class AudioSegment:

    index: int
    path: str
    start_time: datetime
    end_time: datetime = None

    @property
    def duration(self):
        if not self.end_time:
            return 0

        return (
            self.end_time - self.start_time
        ).total_seconds()