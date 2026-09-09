def export_txt(
    path,
    result,
):
    content = f"""OfflineVoice 转写结果

模型：{result["model"]}
设备：{result["device"]}
计算类型：{result["compute_type"]}
语言：{result["language"]}

音频长度：{result["audio_duration"]:.2f} 秒
识别耗时：{result["recognize_time"]:.2f} 秒
实时速度：{result["speed"]:.2f} x
内存：{result["memory"]:.2f} MB

====================

识别内容：

{result["text"]}
"""

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(content)


def export_markdown(
    path,
    result,
):
    content = f"""# OfflineVoice 转写结果

## 音频信息

- 模型：{result["model"]}
- 设备：{result["device"]}
- 计算类型：{result["compute_type"]}
- 语言：{result["language"]}
- 音频长度：{result["audio_duration"]:.2f} 秒
- 识别耗时：{result["recognize_time"]:.2f} 秒
- 实时速度：{result["speed"]:.2f} x
- 内存：{result["memory"]:.2f} MB

## 转写内容

{result["text"]}
"""

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(content)