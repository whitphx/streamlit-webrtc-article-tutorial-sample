import streamlit as st
from streamlit_webrtc import webrtc_streamer

st.title("My first Streamlit app")
st.write("Hello, world")

"""Media streamings"""
import logging
from pathlib import Path
import uuid
import queue
import cv2
import av
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
webrtc_ctx = webrtc_streamer(
    key="mock",
    mode=WebRtcMode.SENDRECV,
    audio_receiver_size=256,
    video_frame_callback=video_frame_callback, # 画像をそのまま返す
    audio_frame_callback=audio_frame_callback, # 音声ファイルからframeにして返す
    #in_recorder_factory=in_recorder_factory,  #　ここで録音を行う
    rtc_configuration={
        "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
    },
)



###### ここより下触らないで
while st.checkbox('now talking'):
    if webrtc_ctx.audio_receiver:
        try:
            audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
        except queue.Empty:
            logger.warning("Queue is empty. Abort.")
            break

        sound_chunk = pydub.AudioSegment.empty()
        for audio_frame in audio_frames:
            sound = pydub.AudioSegment(
                data=audio_frame.to_ndarray().tobytes(),
                sample_width=audio_frame.format.bytes,
                frame_rate=audio_frame.sample_rate,
                channels=len(audio_frame.layout.channels),
            )
            sound_chunk += sound

###whileループを抜けた時、すなわち録音を終了とした時に以下を実行するように、田村に書いて欲しい！！　            
    sound_chunk.export("test.wav", format="wav")
            

####### ここより上触らないで

st.markdown(
    "The video filter in this demo is based on "
    "https://github.com/aiortc/aiortc/blob/2362e6d1f0c730a0f8c387bbea76546775ad2fe8/examples/server/server.py#L34. "  # noqa: E501
    "Many thanks to the project."
)


