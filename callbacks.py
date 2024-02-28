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

class AudioFrameCallback:
    def __init__(self, state_obj):
        self.state_obj = state_obj
    
    def __call__(self, frame: av.AudioFrame) -> av.AudioFrame:
        if self.state_obj.talk_id is None or self.state_obj.is_recording:
            logging.warning("talk_id is None")
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
        try:
            stream_frame = self.state_obj["audios"][self.state_obj.talk_id][self.state_obj.file_number][self.state_obj.frame_number]
            logging.warning("streaming!!")
        except:
            return silent_audio_frame()  ##honraiha
        if self.state_obj.frame_number <  len(self.state_obj["audios"][self.state_obj.talk_id][self.state_obj.file_number])-1:
            self.state_obj.frame_number += 1
        elif self.state_obj.file_number < len(self.state_obj["audios"][self.state_obj.talk_id])-1:
            logging.warning("totyu")
            self.state_obj.file_number += 1
            self.state_obj.frame_number = 0
        else:
            logging.warning("finished")
            frames = silent_audio_frame()
            frames_byte = np.frombuffer(frames.planes[0].to_bytes(), np.int16)
            for file in self.state_obj["audios"][self.state_obj.talk_id]:
                for frame in file:
                    frames_byte = np.concatenate([frames_byte, np.frombuffer(frame.planes[0].to_bytes(), np.int16)])
                    
            np.save('array.npy', frames_byte)
            self.state_obj.file_number = 0
            self.state_obj.frame_number = 0
            return silent_audio_frame()
        
        logging.warning(str(type(stream_frame)))
        logging.warning("file number: %d", self.state_obj.file_number)
        logging.warning("frame number: %d", self.state_obj.frame_number)
        return stream_frame