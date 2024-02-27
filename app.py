import streamlit as st
from streamlit_webrtc import webrtc_streamer

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import pydub
import logging
from pathlib import Path
import uuid
import queue
import pydub
import os
from aiortc.contrib.media import MediaRecorder  # noqa: E402
from langchain import PromptTemplate

import av
from pydub import AudioSegment
import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from callbacks import video_frame_callback, audio_frame_callback, RESPONSE_DIR
from services import save_audio_frames_in_memory, speech_to_text, get_state
from generate_questions import generate_questions
from interview_chat import generate_response

"""Media streamings"""
st.title("My first Streamlit app")
st.write("Hello, world")

HERE = Path(__file__).parent
ROOT = HERE.parent

logger = logging.getLogger(__name__)


#　録音周りの設定
RECORD_DIR = Path("./records")
os.makedirs(RECORD_DIR, exist_ok=True)
os.makedirs(RESPONSE_DIR, exist_ok=True)

if "talk_id" not in st.session_state:
    st.session_state["talk_id"] = str(uuid.uuid4())
    st.write("hello")
    st.session_state["sound_chunk"] = pydub.AudioSegment.empty()
talk_id = st.session_state["talk_id"]


###　ユーザー設定
if "prompt" not in  st.session_state:
    #評価基準によって質問の深掘り方が異なる可能性あり
    template = """You are an interviewer. Ask the following questions and after each answer, ask more deeply according to it.
    {questions}

    Current conversation:
    {history}
    Interviewer: {input}
    Interviewee: """

    st.session_state["prompt"] = PromptTemplate(
        input_variables=["questions","history","input"],
        template=template
    )
if "question" not in  st.session_state:
    company = ''
    n_query = 5
    st.session_state["question"] = generate_questions(company, n_query)




###　ここのコンポーネントでは、ファイルから音声をストリーミングするのと、カメラで読み取った映像を（そのまま）流すことができる。　
main_webrtc_ctx = webrtc_streamer(
    key="mock",
    mode=WebRtcMode.SENDRECV,
    video_frame_callback=video_frame_callback, # 画像をそのまま返す
    audio_frame_callback=audio_frame_callback, # 音声ファイルからframeにして返す
    rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    },
)
# if not main_webrtc_ctx.video_receiver:
#      main_webrtc_ctx.video_receiver.start()

#  録音


# def on_audio_ended():
#     sound_chunk.export("test.wav", format="wav")
#     logger.warning("Audio file is saved.")

webrtc_ctx = webrtc_streamer(
    key="sendonly-audio",
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=256,
    rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    },
    media_stream_constraints={"audio": True},
    # on_audio_ended=on_audio_ended
)

while webrtc_ctx.audio_receiver:
    try:
        audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
    except queue.Empty:
            logger.warning("Queue is empty. Abort.")
            break
    for audio_frame in audio_frames:
        sound = pydub.AudioSegment(
        data=audio_frame.to_ndarray().tobytes(),
        sample_width=audio_frame.format.bytes,
        frame_rate=audio_frame.sample_rate,
        channels=len(audio_frame.layout.channels),
        )
        st.session_state["sound_chunk"] += sound
            
user_text = speech_to_text(st.session_state["sound_chunk"])
state = get_state()
generate_response(st.session_state["prompt"], st.session_state["questions"], user_text, state, handler)
logger.warning("Audio file is saved.")
sound_chunk = pydub.AudioSegment.empty()
st.session_state["talk_id"] = str(uuid.uuid4())
