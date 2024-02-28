import speech_recognition as sr
import io
import pydub
import ssl
import requests
import os
import av
from dotenv import load_dotenv
load_dotenv()
ssl._create_default_https_context = ssl._create_unverified_context

FRAME_SETTINGS = {
            "samples": 960,
            "sample_format": "s16",
            "channels": 2,
            "sample_rate": 48000,
        }

# サンプルフォーマットが"s16"の場合、1サンプルあたり2バイトを使用
bytes_per_sample = 2

# 無音データを生成
silent_data = bytes(FRAME_SETTINGS["channels"] * FRAME_SETTINGS["samples"] * bytes_per_sample)

# av.AudioFrameに無音データを設定
silent_frame = av.AudioFrame(format=FRAME_SETTINGS["sample_format"], layout='stereo', samples=FRAME_SETTINGS["samples"])
silent_frame.rate = FRAME_SETTINGS["sample_rate"]

print(type(silent_frame) is av.audio.frame.AudioFrame)