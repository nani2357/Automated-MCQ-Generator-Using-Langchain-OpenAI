import os
import json
import pandas as pd
import traceback
import PyPDF2


def read_file(file):
    if file.name.lower().endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfFileReader(file)
            text = ""
            for page in range(pdf_reader.getNumPages()):
                page_text = pdf_reader.getPage(page).extract_text()
                if page_text:
                    text += page_text
            return text
        except Exception as e:
            raise Exception(f"Error reading the PDF file: {str(e)}")
    elif file.name.lower().endswith(".txt"):
        try:
            return file.read().decode("utf-8")
        except Exception as e:
            raise Exception(f"Error decoding the TXT file: {str(e)}")
    else:
        raise Exception("Unsupported file format. Only PDF or TXT files are supported.")




"""def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader=PyPDF2.PdfFileReader(file)
            text=""
            for page in pdf_reader.pages:
                text+=page.extract_text()
            return text
        
        except Exception as e:
            raise Exception("error reading the PDF file")
        
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    
    else:
        raise Exception(
            "unsupported file format only PDf or text file supported"
        )"""
        
 
 
 
        
def get_table_data(quiz_str):
    try:
        quiz_dict = json.loads(quiz_str)
        quiz_table_data = []

        for key, value in quiz_dict.items():
            mcq = value["mcq"]
            options = " || ".join(
                [f"{option}-> {option_value}" for option, option_value in value["options"].items()]
            )
            correct = value["correct"]
            quiz_table_data.append({"MCQ": mcq, "Choices": options, "Correct": correct})

        return quiz_table_data

    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False
    

def process_and_save_quiz_data(quiz_str, filename=".csv"):
    # Call the function to get table data
    table_data = get_table_data(quiz_str)

    # Check if table_data was successfully generated
    if table_data:
        try:
            quiz_df = pd.DataFrame(table_data)
            quiz_df.to_csv(filename, index=False)
            print("Data saved successfully.")
        except Exception as e:
            print("Failed to save data to CSV.")
            traceback.print_exception(type(e), e, e.__traceback__)
    else:
        print("Failed to process quiz data.")


"""def get_table_data(quiz_str):
    try:
        quiz_dict = json.loads(quiz_str)
        quiz_table_data=[]
        
        
        for key,value in quiz_dict.items():
            mcq=value["mcq"]
            options = " || ".join(
                [
                    f"{option}-> {option_value}" for option, option_value in value["options"].items()
                ]
            )
            
            correct = value["correct"]
            quiz_table_data.append({"MCQ":mcq, "Choices":options, "Correct":correct})
        return quiz_table_data        
        
        
        
    except Exception as e:
        traceback.print_exception(type(e),e,e.__traceback__)
        return False"""