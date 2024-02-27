from langchain. chat_models import ChatOpenAI
from langchain import PromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import (
    HumanMessage,
)
from langchain.chains import ConversationChain, LLMChain
from langchain.memory import ConversationBufferMemory
import openai
from typing import Any, Dict, List, Tuple
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser


class Evaluation(BaseModel):
    explainingWithCustomerFeedback: Tuple[int, str] = Field(description="Explaining while checking the customer's expressions and reactions.")
    clearCommunicationMinimalJargon: Tuple[int, str] = Field(description="Communicated clearly, using as little jargon as possible.")
    empathyOrCommonGroundGained: Tuple[int, str] = Field(description="Gained empathy or common ground.")
    negotiationContentPurposeConfirmed: Tuple[int, str] = Field(description="Confirmed the content and purpose of the negotiation.")
    negotiationTimeConfirmed: Tuple[int, str] = Field(description="Confirmed the negotiation time.")
    participantsConfirmed: Tuple[int, str] = Field(description="Confirmed the participants.")
    appointmentRequestReasonCommunicated: Tuple[int, str] = Field(description="Clearly communicated the reason for requesting the appointment.")
    preliminaryClosingStrategy: Tuple[int, str] = Field(description="Preliminary closing (aligning post-discussion images) e.g., \"If Mr./Ms. XX feels the value of our service, what kind of action would you expect?\"")
    discussionAgendaArticulated: Tuple[int, str] = Field(description="Articulated the agenda of the discussion.")
    completeCompanyIntroductionGiven: Tuple[int, str] = Field(description="Explained the company introduction without omissions, as per the template.")
    briefHearingReasonsQuestionsStated: Tuple[int, str] = Field(description="Stated the reasons and number of questions for the brief hearing, and confidently proceeded with the hearing.")
    allHearingItemsCovered: Tuple[int, str] = Field(description="Managed to ask all the pre-prepared hearing items without omissions.")
    questionsShowPriorResearch: Tuple[int, str] = Field(description="Asked in a manner that shows prior research has been done (or familiarity with the subject area).")
    storyFlowQuestioning: Tuple[int, str] = Field(description="Explained in a way that the questions flowed as a story without disruption.")
    postHearingThanksAndUtilityExplained: Tuple[int, str] = Field(description="After all questions, articulated thanks and how the content of the brief hearing would be useful in the subsequent service explanation.")


def evaluate(rubric):
    llm = ChatOpenAI(
        #model_name='gpt-4',
        temperature=0.2,
        streaming=True,
    )
    template = """I would like you to mark an interview. Each interview is assigned a rating of 0 to 9, with 9 being the highest and 0 the lowest.
    The interview is scored based on the following rubric.
    {rubric}

    Interview:
    {history}
    """

    prompt = PromptTemplate(
        input_variables=['rubric','history'],
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
        st.session_state.state = {"memory": ConversationBufferMemory(memory_key="history",ai_prefix='Interviewer', human_prefix='Interviewee')}
    return st.session_state.state

rubric = ""
output = evaluate(rubric)
