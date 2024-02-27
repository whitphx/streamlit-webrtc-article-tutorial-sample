"""Media streamings"""
import logging
from pathlib import Path

import av
import pydub
import numpy as np

import streamlit as st


HERE = Path(__file__).parent
ROOT = HERE.parent

logger = logging.getLogger(__name__)


def video_frame_callback(frame: av.VideoFrame) -> av.VideoFrame:
    img = frame.to_ndarray(format="bgr24")
    
    return av.VideoFrame.from_ndarray(img, format="bgr24")


def silent_audio_frame(frame: av.AudioFrame) -> av.AudioFrame:
    samples = frame.samples
    sample_format = frame.format.name
    channels = len(frame.layout.channels)
    sample_rate = frame.sample_rate
    
    # 無音のデータを作成
    silent_data = bytes(channels * samples * av.audio.sample_fmt_to_bytes(sample_format))

    # 無音のav.AudioFrameを作成
    silent_frame = av.AudioFrame(format=sample_format, layout='stereo', samples=samples, sample_rate=sample_rate)
    
    # 無音のデータをセット
    silent_frame.planes[0].update(silent_data)
    
    return silent_frame

def audio_frame_callback(frame: av.AudioFrame) -> av.AudioFrame:
    if st.session_state.recording:
        return silent_audio_frame(frame)
    
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
            ・今再生するべき音声ファイルのディレクトリ名、すなわち会話のID
            ・再生している音声ファイルの番号
            ・再生している音声ファイルのフレーム位置
            ・返信音声が全てファイルかされているかどうか
        """
    