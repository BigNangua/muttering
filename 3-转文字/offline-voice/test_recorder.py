import time

from app.recorder.recorder import Recorder


def on_segment(segment):

    print(
        "新片段:",
        segment.path
    )


recorder = Recorder(
    interval_minutes=1
)

recorder.segment_created.connect(
    on_segment
)


print("开始录音")

recorder.start()


time.sleep(
    130
)


print("停止录音")

recorder.stop()