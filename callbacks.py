"""Media streamings"""
import logging
from pathlib import Path

import av
import pydub
import os
import numpy as np


import cv2
import streamlit as st
from PIL import Image


RESPONSE_DIR = Path("./responses")

FRAME_SETTINGS = {
            "samples": 960,
            "sample_format": "s16",
            "channels": 2,
            "sample_rate": 48000,
        }

logger = logging.getLogger(__name__)


def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")
    
    return av.VideoFrame.from_ndarray(img, format="bgr24")


def silent_audio_frame(sample_rate=48000, channels=2, sample_format="s16", samples=960):
    # フレームの設定に基づいて無音データを生成
    frame = av.AudioFrame(format=sample_format, layout='stereo', samples=samples)
    frame.rate = sample_rate
    # 無音データでフレームを埋める
    silent_data = bytes(channels * samples * 2) # "s16"フォーマットは2バイト
    for plane in frame.planes:
        plane.update(silent_data)
    return frame

def audio_frame_callback(frame: av.AudioFrame) -> av.AudioFrame:
    if st.session_state.recording or "talk_id" not in st.session_state:
        return silent_audio_frame()
    
    else :
        """
            ここで行われること
            ・現在流している音声ファイルとその位置を把握
            
            ・音声が続く場合、その音声を流す
            ・音声が終わった場合、次の音声を流す
            ・まだ収録していない場合、全て再生し終わった場合、無音を返す
            ・収録が終わっているが音声ファイルが一つもない場合、時間稼ぎファイルの音を流す
            ・収録が終わっている音声ファイルがある場合、その音声ファイルを流す
            ・途中でファイルの生成が追いつかなかった場合も無音を返す
           
           
           ファイルの構成
           ・一つの発言につき一つのディレクトリ
              ・そのディレクトリ内には、その発言の音声ファイルが連番で配置される
              
           session_stateとして持つべきもの
            ・talk_id(uuid): 今再生するべき音声ファイルのディレクトリ名、すなわち会話のID
            ・file_number: 再生している音声ファイルの番号
            ・frame_number: 再生している音声ファイルのフレーム位置
            ・is_finished: 返信音声が全てファイルかされているかどうか
        """
        if "file_number" not in st.session_state:
            st.session_state["file_number"] = 0
        if "frame_number" not in st.session_state:
            st.session_state["frame_number"] = 0
        if "is_finished" not in st.session_state:
            st.session_state["is_finished"] = False
        
        
        stream_frame = st.session_state[st.session_state["talk_id"]][st.session_state["file_number"]][st.session_state["frame_number"]]
        if st.session_state["frame_number"] <  len(st.session_state[st.session_state["talk_id"]][st.session_state["file_number"]])-1:
            st.session_state["frame_number"] += 1
        elif st.session_state["file_number"] < len(st.session_state[st.session_state["talk_id"]])-1:
            st.session_state["file_number"] += 1
            st.session_state["frame_number"] = 0
        else:
            st.session_state["file_number"] = 0
            st.session_state["frame_number"] = 0
            st.session_state["is_finished"] = True
            return silent_audio_frame(frame)
        
        return stream_frame