import streamlit as st
from streamlit_webrtc import webrtc_streamer

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

st.title("My first Streamlit app")
st.write("Hello, world")

"""Media streamings"""
import pydub
import logging
from pathlib import Path
import uuid
import queue
import pydub
import os
from aiortc.contrib.media import MediaRecorder  # noqa: E402

import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from callbacks import video_frame_callback, audio_frame_callback


HERE = Path(__file__).parent
ROOT = HERE.parent

logger = logging.getLogger(__name__)


#　録音周りの設定
RECORD_DIR = Path("./records")
os.makedirs(RECORD_DIR, exist_ok=True)

#初回
if "talk_id" not in st.session_state:
    st.session_state["talk_id"] = str(uuid.uuid4())
    st.write("hello")
    st.session_state["sound_chunk"] = pydub.AudioSegment.empty()
talk_id = st.session_state["talk_id"]



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

#  録音
webrtc_ctx = webrtc_streamer(
    key="sendonly-audio",
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=256,
    rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    },
    media_stream_constraints={"audio": True},
)

while True:
    if webrtc_ctx.state.playing:
        if "is_first" not in st.session_state:
            st.session_state["is_first"] = True
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
    else:
        logger.warning("Audio receiver is not set. Abort.")
        break
#これだと、画面が開いた時にexportしてしまう
if "is_first" not in st.session_state:
    st.session_state["sound_chunk"].export(f"{str(RECORD_DIR)}/{st.session_state.talk_id}.wav", format="wav")
    logger.warning("Audio file is saved.")
    sound_chunk = pydub.AudioSegment.empty()
st.session_state["talk_id"] = str(uuid.uuid4())
