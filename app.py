import streamlit as st
from streamlit_webrtc import webrtc_streamer
import time

from dotenv import load_dotenv
load_dotenv()


import pydub
import logging
from pathlib import Path
import uuid
import queue
import pydub
import os
from langchain import PromptTemplate

import streamlit as st
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from callbacks import video_frame_callback, RESPONSE_DIR, AudioFrameCallback
from services import save_audio_frames_in_memory, speech_to_text, get_state
from generate_questions import generate_questions
from generate_eval import generate_eval
from interview_chat import generate_response
#from interview_eval import eval

from states import StatesObject
from common_questions import common_questions

HERE = Path(__file__).parent
ROOT = HERE.parent

logger = logging.getLogger(__name__)



#　録音周りの設定
RECORD_DIR = Path("./records")
os.makedirs(RECORD_DIR, exist_ok=True)
os.makedirs(RESPONSE_DIR, exist_ok=True)

#初回
if "talk_id" not in st.session_state:
    st.session_state["talk_id"] = None
    st.write("hello")
    st.session_state["sound_chunk"] = pydub.AudioSegment.empty()
    st.session_state["is_recording"] = False
    st.session_state["is_interview_finished"] = False#移したほうがいいかも
    st.session_state["count"] = 0
talk_id = st.session_state["talk_id"]
st.write(st.session_state["talk_id"])


if 'is_interview_ongoing' not in st.session_state:
    st.session_state['is_interview_ongoing'] = False

if 'is_started' not in st.session_state:
    st.session_state['is_started'] = False


def on_interview_finished():
        logger.warning("面接を終了")
        st.session_state['is_interview_ongoing'] = False
        logger.warning(st.session_state['is_interview_ongoing'])
        st.session_state['is_interview_finished'] = True
        
        # rubric = { 
        
        # }
        # st.session_state['eval'] = eval(rubric, examples=None)
        
if st.session_state['is_interview_ongoing']:
    st.button("面接終了", on_click=on_interview_finished)


elif not st.session_state['is_interview_finished']:
    if st.button("面接を開始する"):
        if "company_name" in st.session_state and "position" in st.session_state and "desired_candidate_character" in st.session_state and "additional_info" in st.session_state:
            recruitInfo = {
                "company_name": st.session_state["company_name"],
                "position": st.session_state["position"],
                "desired_candidate_character": st.session_state["desired_candidate_character"],
                "additional_info": st.session_state["additional_info"],
            }

            st.session_state["questions"] = generate_questions(recruitInfo, n_query=3)
            # unique_criteria = generate_eval(st.session_state["company_attributes"], examples=None)#評価基準を生成する
            

            
            st.write(st.session_state["questions"])
            ###　ユーザー設定
            if "questions" in st.session_state and "prompt" not in  st.session_state:
                template = f"""You are an interviewer. Ask the following questions and after each answer, ask more deeply according to it.
                                {st.session_state["questions"]}+{common_questions}""" + \
                                """Current conversation:
                                {history}
                                Interviewer: {input}
                                Interviewee: """
                questions = ""
                st.session_state["prompt"] = PromptTemplate(
                    input_variables=["history","input"],
                    template=template
                )
            st.write(st.session_state['is_interview_ongoing'])
            st.session_state['is_interview_ongoing'] = True
            st.write(st.session_state['is_interview_ongoing'])
        else:
            st.write("Please fill in all the settings.")
else:
    st.write("模擬面接は終了です！お疲れ様でした！")


###　ここのコンポーネントでは、ファイルから音声をストリーミングするのと、カメラで読み取った映像を（そのまま）流すことができる。　
if not st.session_state['is_interview_finished']:    
    state_obj = StatesObject()
    state_obj.set_talk_id(st.session_state["talk_id"])
    audio_frame_callback = AudioFrameCallback(state_obj)
    main_webrtc_ctx = webrtc_streamer(
        key="mock",
        mode=WebRtcMode.SENDRECV,
        video_frame_callback=video_frame_callback, # 画像をそのまま返す
        audio_frame_callback=audio_frame_callback, # 音声ファイルからframeにして返す
        rtc_configuration={
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        },
        desired_playing_state=st.session_state['is_interview_ongoing'],
        media_stream_constraints={"video": True, "audio": True},
)


    if main_webrtc_ctx.state.playing:
        if not st.session_state["is_started"]:
            st.write("元気よく挨拶をしてみましょう！")
        #  録音
        webrtc_ctx = webrtc_streamer(
            key="sendonly-audio",
            mode=WebRtcMode.SENDONLY,
            audio_receiver_size=256,
            rtc_configuration={
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            },
            media_stream_constraints={"audio": True},
            translations={
                "start": "録音開始",
                "stop": "録音終了",
            }
        )
        if not st.session_state["is_recording"]:
            st.session_state['is_recording'] = webrtc_ctx.state.playing
            st.session_state['count'] += 1

            

        while True:
            if webrtc_ctx.state.playing:
                if state_obj.get_talk_id() is None:
                    st.session_state["talk_id"] = str(uuid.uuid4())
                    state_obj.set_talk_id(st.session_state["talk_id"])
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

        if len(st.session_state["sound_chunk"]) > 0:
            user_text = speech_to_text(st.session_state["sound_chunk"])
            state = get_state()
            if not st.session_state["is_started"]:
                st.session_state["is_started"] = True
            
            result_area = st.empty()
            generate_response(st.session_state["prompt"], user_text, state, state_obj, result_area)
            logger.warning("Audio file is saved.")
            sound_chunk = pydub.AudioSegment.empty()
            st.session_state["talk_id"] = None
        else:
            print("No sound is recorded.")
    else:
        st.write("Settings")
        company_name = st.text_input("Company Name", value="")
        position = st.text_input("Position", value="")
        desired_candidate_character = st.text_area("Desired Candidate Character", value="")
        additional_info = st.text_area("Additional Info", value="")

        # Update session state with the input values if needed
        if company_name:
            st.session_state["company_name"] = company_name
        if position:
            st.session_state["position"] = position
        if desired_candidate_character:
            st.session_state["desired_candidate_character"] = desired_candidate_character
        if additional_info:
            st.session_state["additional_info"] = additional_info

        
