from langchain.chat_models import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.output_parsers import PydanticOutputParser
from typing import List
import json
import streamlit as st


def generate_questions(recruitInfo, n_query, examples=None):
    instruction = f"Generate {n_query} questions which are likely to be asked in the interview at the following company and put them. Please note that questions should be unique to the company: "

    template = """{instruction}\n{company}"""
    prompt = PromptTemplate(
        template=template,
        input_variables=["instruction","company"],
    ).format_prompt(instruction=instruction, company=json.dumps(recruitInfo))
    llm = OpenAI(temperature=1)
    output = llm(prompt.to_string())
    return output

# n_query = 5
# st.session_state['company_attributes'] = {
#     'name': "softbank",
#     'position' : "Data Scientist",
#     'required_personalities' : 'team player, self-starter, problem solver',
# }

# questions = generate_questions(st.session_state['company_attributes'], n_query)