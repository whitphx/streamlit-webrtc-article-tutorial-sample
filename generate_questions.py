from langchain.chat_models import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.output_parsers import PydanticOutputParser
from typing import List
import json

class Company(BaseModel):
    """事前情報として与えたい会社情報"""
    pass

class ES(BaseModel):
    """エントリーシート"""
    pass


def generate_questions(company, n_query, examples=None):
    instruction = f"Generate {n_query} questions which are likely to be asked in the interview at the following company:"
    template = """{instruction}\n{company}"""
    prompt = PromptTemplate(
        template=template,
        input_variables=["instruction","company"],
    ).format_prompt(instruction=instruction, company=company)
    llm = OpenAI(temperature=1)
    output = llm(prompt.to_string())
    return output


n_query = 5
company_attributes = {
    'name': "Softbank",
    #and so on
}

company = Company(**company_attributes)
questions = generate_questions(company, n_query)