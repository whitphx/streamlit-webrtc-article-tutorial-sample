from langchain. chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import (
    HumanMessage,
)
from langchain.chains import ConversationChain, LLMChain
import openai
from typing import Any, Dict, List
import streamlit as st
import os
import requests
import av

from generate_questions import generate_questions
from services import text_to_speech
import speech_recognition as sr


#これもAsyncにできる？
class SentenceCallbackHandler(BaseCallbackHandler):
    """ Sentence Callback Handler """

    def __init__(self, model='tts-1', voice='alloy', response_format="opus") -> None:
        self.sentence = ''
        self.model = model
        self.voice = voice
        self.response_format = response_format

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        self.sentence += token

        #一文になったら非同期でself.sentenceをtext_to_speechに(下は仮)
        if token in ['.','?','!']:
            #print(self.sentence)
            text_to_speech(self.sentence, self.model, self.voice, self.response_format)
            self.sentence = ''
            
    def on_llm_end(self, **kwargs: Any) -> None:
        """Run on LLM end. Only available when streaming is enabled."""
        st.session_state["is_finished"] = True
        



profile = {
    'model': 'tts-1',
    'voice': 'alloy',
    'response_format': "opus",
}



handler = SentenceCallbackHandler(**profile)


def generate_response(prompt, questions, user_input, state, handler):
    llm = ChatOpenAI(streaming=True, temperature=0.9)
    conversation = ConversationChain(
        llm=llm,
        prompt=prompt,
        memory=state['memory']
    )
    res = conversation.predict(questions=questions, input=user_input, callback=[handler])
    return None