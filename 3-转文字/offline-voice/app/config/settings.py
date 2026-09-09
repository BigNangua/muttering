import os
import json


CONFIG_FILE = "data/settings.json"


# 录音参数
SAMPLE_RATE = 16000
CHANNELS = 1


def load_settings():
    if not os.path.exists(CONFIG_FILE):
        return {
            "model": "medium",
            "segment_seconds": 120,
        }

    try:
        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            return json.load(f)

    except Exception:
        return {
            "model": "medium",
            "segment_seconds": 120,
        }


def save_settings(settings):
    os.makedirs(
        os.path.dirname(CONFIG_FILE),
        exist_ok=True
    )

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            settings,
            f,
            ensure_ascii=False,
            indent=4
        )


def get_model():
    settings = load_settings()

    return settings.get(
        "model",
        "medium"
    )


def get_settings():
    return load_settings()


def get_segment_seconds():
    settings = load_settings()

    return settings.get(
        "segment_seconds",
        120
    )


SEGMENT_SECONDS = get_segment_seconds()


def get_available_models():

    model_dir = (
        "models/whisper"
    )

    if not os.path.exists(model_dir):
        return []

    models = []

    for name in os.listdir(model_dir):
        path = os.path.join(
            model_dir,
            name
        )

        if os.path.isdir(path):
            models.append(name)

    return models