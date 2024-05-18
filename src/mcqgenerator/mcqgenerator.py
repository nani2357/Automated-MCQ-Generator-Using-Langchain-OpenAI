import os
import json
import pandas as pd
import traceback
import langchain
import openai
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain.callbacks import get_openai_callback



from langchain_community.chat_models import ChatOpenAI

load_dotenv()
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY. Check your .env file.")

try:
    llm = ChatOpenAI()  # Using simplified constructor if applicable
except Exception as e:
    traceback.print_exception(type(e), e, e.__traceback__)
    raise Exception("Failed to initialize language model interface.") from e


#prompt = "what is open banking, give list of compiens in UK "
#output2 = llm.invoke(prompt)
#print(f"output2 : {output2}")

TEMPLATE="""
Text:{text}
You are an expert multiple choice questions(MCQ) maker. Given the above text, it is your job to \
create a quiz  of {number} multiple choice questions for {subject} students in {tone} tone. 
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like  RESPONSE_JSON below  and use it as a guide. \
Ensure to make {number} MCQs
### RESPONSE_JSON
{response_json}

"""

TEMPLATE2="""
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Use {text} for complexity analysis. 
if the quiz is not at per with the cognitive and analytical abilities of the students,\
update the quiz questions which needs to be changed and change the tone such that it perfectly fits the student abilities
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=TEMPLATE
    )

quiz_evaluation_prompt=PromptTemplate(
    input_variables=["text","subject", "quiz"],
    template=TEMPLATE2
    )

quiz_chain = LLMChain(llm=llm, prompt=quiz_generation_prompt,output_key='quiz',verbose=True)
review_chain=LLMChain(llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True)


generate_evaluate_chain=SequentialChain(
    chains=[quiz_chain, review_chain],
    input_variables=["text", "number", "subject", "tone", "response_json"],
    output_variables=["quiz", "review"], verbose=True,)




