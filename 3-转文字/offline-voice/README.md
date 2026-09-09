我给你整理成适合 **OfflineVoice 当前项目状态** 的 README.md。

包含：

* Windows 环境
* 创建项目目录
* 创建虚拟环境
* 激活 `.venv`
* 安装依赖
* 下载/准备 Whisper 模型
* 模型目录说明
* 启动程序
* 功能说明
* 打包 EXE
* 常见问题

保存为：

```
D:\work\offline-voice\README.md
```

内容如下：

# OfflineVoice

OfflineVoice 是一个离线语音转文字工具。

主要功能：

- 麦克风实时录音
- 录音过程中自动分段识别
- 会议实时转文字
- 保存原始录音
- 导入音频文件转文字
- TXT / Markdown 导出
- 本地 Whisper 模型离线运行
- 支持 small / medium 模型切换


---

# 一、环境要求

## 操作系统

目前支持：

- Windows 10
- Windows 11


## Python版本

推荐：

Python 3.10.x

检查：

```powershell
python --version
```

示例：

```
Python 3.10.8
```

---

# 二、创建项目目录

例如：

```powershell
D:
cd D:\work

mkdir offline-voice

cd offline-voice
```

进入项目目录：

```powershell
cd D:\work\offline-voice
```

注意：

必须先进入项目目录，再创建虚拟环境。

---

# 三、创建 Python 虚拟环境

在项目根目录执行：

```powershell
python -m venv .venv
```

完成后目录结构：

```
offline-voice

├── .venv
├── app
├── models
├── data
├── tests
└── README.md
```

---

# 四、激活虚拟环境

PowerShell：

```powershell
.\.venv\Scripts\activate
```

成功后：

```
(.venv) PS D:\work\offline-voice>
```

说明：

当前已经进入虚拟环境。

以后运行项目前都需要：

```powershell
cd D:\work\offline-voice

.\.venv\Scripts\activate
```

---

# 五、安装依赖

升级 pip：

```powershell
python -m pip install --upgrade pip
```

安装依赖：

```powershell
pip install -r requirements.txt
```

如果没有 requirements.txt：

安装核心依赖：

```powershell
pip install faster-whisper

pip install PySide6

pip install sounddevice

pip install soundfile

pip install psutil
```

---

# 六、FFmpeg安装

部分音频格式需要 FFmpeg。

支持：

* mp3
* m4a
* flac
* wav
* aac

下载后，例如：

```
D:\ffmpeg
```

加入环境变量：

```
D:\ffmpeg\bin
```

检查：

```powershell
ffmpeg -version
```

出现版本信息说明成功。

---

# 七、Whisper模型

OfflineVoice 使用：

```
faster-whisper
```

模型支持：

* small
* medium

模型必须放置：

```
models

└── whisper

    ├── small

    │   ├── config.json
    │   ├── model.bin
    │   ├── tokenizer.json
    │   └── vocabulary.txt


    └── medium

        ├── config.json
        ├── model.bin
        ├── tokenizer.json
        └── vocabulary.txt
```

例如：

```
D:\work\offline-voice\models\whisper\medium
```

---

# 八、模型扫描

程序启动后会自动扫描：

```
models/whisper/
```

例如：

发现：

```
models/whisper/medium
```

设置页面会显示：

```
medium
```

用户可以切换：

```
small
medium
```

切换后：

* 导入识别使用该模型
* 录音实时识别使用该模型

---

# 九、启动程序

进入项目目录：

```powershell
cd D:\work\offline-voice
```

激活环境：

```powershell
.\.venv\Scripts\activate
```

启动：

```powershell
python -m app.main
```

正常启动：

```
OfflineVoice
```

---

# 十、功能说明

## 1. 录音转文字

流程：

```
开始录音

↓

麦克风采集

↓

每 N 分钟保存一个音频片段

↓

Whisper识别

↓

文字显示

↓

会议结束

↓

保存完整录音和文字
```

默认：

```
60秒
```

可以在设置修改：

例如：

```
120秒
```

表示：

每2分钟识别一次。

---

# 2. 麦克风权限

录音采用：

```
sounddevice InputStream
```

方式：

共享模式。

不会：

* 独占麦克风
* WASAPI Exclusive
* 禁止其他软件使用

因此：

可以同时打开：

* 微信会议
* 腾讯会议
* 浏览器录音

---

# 3. 导入音频识别

流程：

```
选择音频

↓

开始识别

↓

加载设置模型

↓

显示文字

↓

导出
```

支持：

```
wav
mp3
m4a
flac
aac
ogg
wma
```

---

# 4. 导出

支持：

TXT：

```
xxx.txt
```

Markdown：

```
xxx.md
```

导出内容：

只包含：

* 转写文字

不包含：

* CPU
* 内存
* 模型
* 设备信息

---

# 十一、项目结构

```
offline-voice

├── app

│
├── asr

│   └── engine.py
│
├── audio

│   ├── recorder.py
│   └── recording_service.py
│
├── config

│   └── settings.py
│
├── core

│   └── app_state.py
│
├── export

│   └── exporter.py
│
├── storage

│   └── recording_storage.py
│
├── ui

│   ├── main_window.py
│   │
│   ├── pages
│   │
│   │   ├── record_page.py
│   │   ├── import_page.py
│   │   └── settings_page.py
│
└── workers

    ├── asr_worker.py
    └── recording_asr_worker.py


├── data

│
└── models

    └── whisper

```

---

# 十二、打包 EXE

安装 PyInstaller：

```powershell
pip install pyinstaller
```

检查：

```powershell
pyinstaller --version
```

---

# 十三、生成EXE

项目目录：

```powershell
cd D:\work\offline-voice
```

执行：

```powershell
pyinstaller ^
--name OfflineVoice ^
--windowed ^
--add-data "models;models" ^
--add-data "data;data" ^
app/main.py
```

完成后：

```
dist

└── OfflineVoice

    ├── OfflineVoice.exe
    ├── models
    └── data

```

运行：

```
OfflineVoice.exe
```

---

# 十四、完全离线运行

部署电脑：

需要包含：

```
OfflineVoice.exe

models/

data/
```

不需要：

* 网络
* HuggingFace
* 在线API

所有识别：

本地 Whisper 完成。

---

# 十五、常见问题

## 1. QThread错误

错误：

```
QThread: Destroyed while thread is still running
```

原因：

线程没有退出。

解决：

关闭窗口前：

```
worker.stop()
thread.quit()
thread.wait()
```

---

## 2. 找不到模型

检查：

```powershell
Get-ChildItem models\whisper
```

应该看到：

```
medium
small
```

---

## 3. 第一次启动慢

正常。

第一次：

加载模型。

之后：

速度会提升。

---

# 十六、当前版本

版本：

```
OfflineVoice v1.0
```

运行环境：

```
Windows 11
Python 3.10
CPU
faster-whisper
PySide6
```

目标：

完全离线会议语音转文字工具。

```

---

另外建议你下一步做 **打包前最后整理**：

1. `requirements.txt` 固化  
2. `offlinevoice.spec` 写好（否则模型 1.5GB 打包会很麻烦）  
3. 增加 `models` 自动检测  
4. 测试无 Python 环境启动 EXE

现在你的项目已经不是 demo 了，已经接近正式桌面软件结构。下一步应该进入打包和发布阶段。
```
