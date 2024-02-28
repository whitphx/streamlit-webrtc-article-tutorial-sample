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
import logging

from generate_questions import generate_questions
from services import text_to_speech
import speech_recognition as sr


#これもAsyncにできる？
class SentenceCallbackHandler(BaseCallbackHandler):
    """ Sentence Callback Handler """

    def __init__(self, state_obj, result_area, model='tts-1', voice='alloy', response_format="opus") -> None:
        self.state_obj= state_obj
        self.sentence = ''
        self.model = model
        self.voice = voice
        self.response_format = response_format
        self.result_area = result_area

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        self.sentence += str(token)
        self.result_area.write(self.sentence)
        
        #一文になったら非同期でself.sentenceをtext_to_speechに(下は仮)
        if token in ['.','?','!']:
            #print(self.sentence)
            text_to_speech(self.state_obj, self.sentence, self.model, self.voice, self.response_format)
            self.sentence = ''
            
    def on_llm_end(self, response, **kwargs: Any) -> None:
        """Run on LLM end. Only available when streaming is enabled."""
        st.write(response)
        self.state_obj.set_is_finished(True)
        



profile = {
    'model': 'tts-1',
    'voice': 'alloy',
    'response_format': "opus",
}


def generate_response(prompt, user_input, state, state_obj, result_area):
    handler = SentenceCallbackHandler(state_obj, result_area, **profile)
    llm = ChatOpenAI(streaming=True, temperature=0.9, callbacks=[handler])
    conversation = LLMChain(
        llm=llm,
        prompt=prompt,
        memory=state['memory']
    )
    res = conversation.predict(input=user_input)
    return res