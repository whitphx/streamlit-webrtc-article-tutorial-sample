import streamlit as st
from streamlit_webrtc import webrtc_streamer

st.title("My first Streamlit app")
st.write("Hello, world")

"""Media streamings"""
import pydub
import logging
from pathlib import Path
import uuid
import queue
import pydub
from aiortc.contrib.media import MediaRecorder  # noqa: E402

import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from services import video_frame_callback, audio_frame_callback


HERE = Path(__file__).parent
ROOT = HERE.parent

logger = logging.getLogger(__name__)


#　録音周りの設定
RECORD_DIR = Path("./records")

if "prefix" not in st.session_state:
    st.session_state["prefix"] = str(uuid.uuid4())
prefix = st.session_state["prefix"]
in_file = RECORD_DIR / f"{prefix}_input.flv"

def in_recorder_factory() -> MediaRecorder:
    return MediaRecorder(
        str(in_file), format="flv"
    )

###　ここのコンポーネントでは、ファイルから音声をストリーミングするのと、カメラで読み取った映像を（そのまま）流すことができる。　
main_webrtc_ctx = webrtc_streamer(
    key="mock",
    mode=WebRtcMode.SENDRECV,
    video_frame_callback=video_frame_callback, # 画像をそのまま返す
    audio_frame_callback=audio_frame_callback, # 音声ファイルからframeにして返す
    in_recorder_factory=in_recorder_factory,  #　ここで録音を行う
    rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    },
)
if not main_webrtc_ctx.video_receiver:
     main_webrtc_ctx.video_receiver.start()


#  録音
sound_chunk = pydub.AudioSegment.empty()

webrtc_ctx = webrtc_streamer(
    key="sendonly-audio",
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=256,
    rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    },
    media_stream_constraints={"audio": True},
)

while webrtc_ctx.audio_receiver:
    try:
        audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
        logger.info("録音中")
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
            sound_chunk += sound
sound_chunk.export("test.wav", format="wav")
logger.info("Audio file is saved.")