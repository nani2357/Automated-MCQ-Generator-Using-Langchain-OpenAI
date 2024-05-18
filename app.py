import os
import json
import pandas as pd
import traceback
import PyPDF2

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain
from langchain.callbacks import get_openai_callback

from src.mcqgenerator.mcqgenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging
from src.mcqgenerator.utils import read_file, get_table_data, process_and_save_quiz_data

# Load environment variables
load_dotenv()

# Load JSON file
with open('response.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

# Streamlit page configuration
st.set_page_config(page_title="QuizMaster: AI-Powered MCQ Generator", page_icon=":brain:")
st.title("🧠 QuizMaster: Your AI-Powered MCQ Generator 🤖")
st.write("""
Welcome to QuizMaster, the ultimate tool for creating customized multiple-choice questions! 
Whether you're a teacher crafting quizzes or a student prepping for exams, QuizMaster simplifies the process. 
Just paste your content, select a subject, and choose the difficulty level (easy, medium, or hard). 
Specify how many questions you want, and voilà—tailored MCQs are generated instantly! 
This app is designed to save time and enhance learning by providing targeted practice on any topic. 
Dive into a seamless quiz creation experience with QuizMaster!
""")

# User input form
with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Upload a PDF or txt file", type=["pdf", "txt"])
    text_input = st.text_area("Or paste your text here (max 2000 words):", max_chars=15000)
    mcq_counts = st.number_input("Number of MCQs", min_value=5, max_value=30)
    subject = st.text_input("Insert Subject", max_chars=50)
    tone = st.text_input("Complexity Level of Question", max_chars=30, placeholder="Simple")
    button = st.form_submit_button("Create MCQs")

if button:
    error_message = []
    content = None

    # Check file size if a file is uploaded
    if uploaded_file is not None and uploaded_file.size > 2 * 1024 * 1024:  # file size in bytes (2MB)
        error_message.append("File size must be under 2MB.")
    
    # Ensure that only one input method is used
    if (uploaded_file is not None and text_input.strip()) or (uploaded_file is None and not text_input.strip()):
        error_message.append("Please either upload a file or input text, not both.")

    # Check for required inputs
    if not (mcq_counts and subject and tone):
        error_message.append("Please ensure all fields are filled out.")

    if not error_message and uploaded_file is not None:
        with st.spinner("Loading..."):
            try:
                content = read_file(uploaded_file)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Failed to read file.")
    elif not error_message:
        content = text_input.strip()

    if error_message:
        for message in error_message:
            st.error(message)
    elif content:
        with st.spinner("Generating MCQs..."):
            try:
                with get_openai_callback() as cb:
                    response = generate_evaluate_chain({
                        "text": content,
                        "number": mcq_counts,
                        "subject": subject,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                    })
                    st.success("MCQs generated successfully!")
                    # Here, add code to handle and display the response if necessary
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("An error occurred while generating MCQs.")
                
            else:
                # Display token and cost details if required
                st.write(f"Total Tokens: {cb.total_tokens}")
                st.write(f"Prompt Tokens: {cb.prompt_tokens}")
                st.write(f"Completion Tokens: {cb.completion_tokens}")
                st.write(f"Total Cost: {cb.total_cost}")

                if isinstance(response, dict):
                    quiz = response.get("quiz", None)
                    if quiz:
                        table_data = get_table_data(quiz)
                        if table_data:
                            df = pd.DataFrame(table_data)
                            df.index = df.index + 1
                            st.table(df)
                            st.text_area("Review", value=response["review"], height=350)
                            
                            # Convert DataFrame to CSV for download
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="Download MCQs as CSV",
                                data=csv,
                                file_name="mcqs.csv",
                                mime="text/csv",
                            )

                        else:
                            st.error("Error in processing table data")
                else:
                    st.write(response)

# Footer
st.markdown("---")
st.write("© 2024 QuizMaster. All rights reserved. Contact: Naveen Kumar, email: naveenkadampally@gmail.com")
