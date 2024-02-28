import streamlit as st
import av
import requests
import os
import speech_recognition as sr
import pydub
import io
import logging
import ssl
import openai
import numpy as np
ssl._create_default_https_context = ssl._create_unverified_context

from langchain.memory import ConversationBufferMemory


def save_audio_frames_in_memory(states_obj, opus_data: bytes):
    FRAME_SETTINGS = {
            "samples": 960,
            "sample_format": "s16",
            "channels": 2,
            "sample_rate": 48000,
    }
    frames = []
    index = 0
    while index < len(opus_data):
        # サンプル数ごとにデータを取得
        data_chunk = opus_data[index:index + FRAME_SETTINGS["samples"]*4]
        # オーディオフレームに変換してリストに追加
        if len(data_chunk) < FRAME_SETTINGS["samples"]*4:
            break    
        # このコードブロックは仮の例であり、実際のデータ構造に合わせて適宜調整してください。
        array = np.frombuffer(data_chunk, dtype=np.int16).reshape(2, -1)  # ステレオの場合
        frame = av.AudioFrame.from_ndarray(array, format='s16', layout='stereo')
        frames.append(frame)
        index += FRAME_SETTINGS["samples"]
    
    if states_obj.get_talk_id() not in states_obj.audios:
        states_obj.audios[states_obj.get_talk_id()] = []
    states_obj.audios[states_obj.get_talk_id()].append(frames)
    logging.warning("start save audio frames in memory5")
    logging.warning("audio frame length: %d", len(states_obj.audios[states_obj.get_talk_id()]))
    
def speech_to_text(audio_frame):
    return "dummy text for now."
    """
    buffer = io.BytesIO()
    audio_frame.export(buffer, format='wav')
    buffer.name = 'file.wav'
    transcription = openai.audio.transcriptions.create(
        model='whisper-1',
        file=buffer,
        prompt="Umm, let me think like, hmm... Okay, here's what I'm, like, thinking."
    )
    return transcription.text
    """

def text_to_speech(state_obj, text, model='tts-1', voice='alloy', response_format="opus"):
    """" generate and send speech """
    logging.warning("start text to speech")
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    api_url = "https://api.openai.com/v1/audio/speech"
    headers = {
        "Authorization": f'Bearer {api_key}',  # Replace with your API key
    }

    data = {
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": response_format,
    }

    with requests.post(api_url, headers=headers, json=data) as response:
        if response.status_code == 200:
            save_audio_frames_in_memory(state_obj, response.content)
        else:
            response.raise_for_status()
            
def get_state():
    if "state" not in st.session_state:
        st.session_state.state = {"memory": ConversationBufferMemory(memory_key="history",ai_prefix='Interviewer', human_prefix='Interviewee')}
    return st.session_state.state