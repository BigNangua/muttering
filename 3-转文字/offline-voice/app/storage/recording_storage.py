import os
from datetime import datetime


def create_recording_session():
    session_name = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    session_dir = os.path.join(
        "data",
        "recordings",
        session_name,
    )

    os.makedirs(
        session_dir,
        exist_ok=True
    )

    return {
        "name": session_name,
        "directory": session_dir,
        "audio": os.path.join(
            session_dir,
            "audio.wav"
        ),
        "text": os.path.join(
            session_dir,
            "transcript.txt"
        ),
        "markdown": os.path.join(
            session_dir,
            "transcript.md"
        ),
    }


def save_transcript(
    path,
    text,
):
    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(text)


def save_markdown(
    path,
    text,
):
    content = f"""# 会议转写

{text}
"""

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(content)