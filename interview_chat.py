from langchain. chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import (
    HumanMessage,
)
from langchain.chains import ConversationChain, LLMChain
from langchain.memory import ConversationBufferMemory
import openai
from typing import Any, Dict, List
import streamlit as st
import os
import requests

from generate_questions import generate_questions

def text_to_speech(text, model='tts-1', voice='alloy', response_format="opus"):
    """" generate and send speech """
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

    with requests.post(api_url, headers=headers, json=data, stream=True) as response:
        if response.status_code == 200:
            with open('audio.opus', 'wb') as file:
                # opus形式の音声データをファイルに書き込む
                file.write(response.raw)
        else:
            response.raise_for_status()

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
            

def get_state():
    if "state" not in st.session_state:
        st.session_state.state = {"memory": ConversationBufferMemory(memory_key="history",ai_prefix='Interviewer', human_prefix='Interviewee')}
    return st.session_state.state


company = ''
n_query = 5

state = get_state()
user_input = ''
questions = generate_questions(company, n_query)

profile = {
    'model': 'tts-1',
    'voice': 'alloy',
    'response_format': "opus",
}

#評価基準によって質問の深掘り方が異なる可能性あり
template = """You are an interviewer. Ask the following questions and after each answer, ask more deeply according to it.
{questions}

Current conversation:
{history}
Interviewer: {input}
Interviewee: """

prompt = PromptTemplate(
    input_variables=["questions","history","input"],
    template=template
)

handler = SentenceCallbackHandler(**profile)


llm = ChatOpenAI(streaming=True, temperature=0.9)
conversation = ConversationChain(
    llm=llm,
    prompt=prompt,
    memory=state['memory']
)
res = conversation.predict(questions=questions, input=user_input, callback=[handler])
