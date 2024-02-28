from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import HumanMessage
from langchain.chains import ConversationChain, LLMChain
from langchain.memory import ConversationBufferMemory
import openai
from typing import Any, Dict, List, Tuple
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
import streamlit as st
import json  # Import json for handling JSON objects

def evaluate(unique_rubric):#generate_evalの出力を代入
    llm = ChatOpenAI(
        temperature=0.2,
        streaming=True,
    )
    # Define common_rubric as specified
    common_rubric = {
        "Clarity": "Whether the opinion is expressed concisely",
        "Comprehension": "Am I understanding the intent of the question correctly?"
        }
    # Combine unique_rubric and common_rubric
    rubric = {**unique_rubric, **common_rubric} 
    
    rubric_str = json.dumps(rubric, ensure_ascii=False, indent=2)  # Convert the combined rubric to a string for the template

    template = """You are a specialist of job interview specialist. I would like you to mark an interview. Each interview is assigned a rating of 0 to 10, with 10 being the highest and 0 the lowest.
    The interview is scored based on the following rubric.
    {rubric}

    Interview:
    {history}
    """

    prompt = PromptTemplate(
        input_variables=['rubric', 'history'],
        memory=get_state()['memory'],
        template=template,
    )
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
    )
    output = chain.predict(rubric=rubric)
    return output

def get_state():
    if "state" not in st.session_state:
        st.session_state.state = {"memory": ConversationBufferMemory(memory_key="history", ai_prefix='Interviewer', human_prefix='Interviewee')}
    return st.session_state.state
