import os
import openai
from openai import OpenAI
import datetime
from typing import List
import pymupdf4llm
import pathlib

from pydantic import BaseModel, Field

# from langchain.evaluation.parsing.json_distance import JsonEditDistanceEvaluator

class InsuranceForm(BaseModel):
    form_number: str
    form_title: str

class EndorsementForm(BaseModel):
    endorsement_number: str
    endorsement_title: str

class InsurancePolicyData(BaseModel):
    number: str
    start_date: str
    end_date: str
    premium: float
    forms_and_endorsements: List[InsuranceForm]
    # forms_and_endorsements: List[InsuranceForm] = Field(..., description="The forms/endorsements can be present in multiple different locations. Consider all unique forms/endorsements over the entire text.")
    # endorsements: List[EndorsementForm] = Field(..., description="The endorsement forms can be present in multiple different locations. Count all unique endorsements over the entire text.")

def ask_question_about_pdf(pdf_text: str) -> str:
    """
    Upload text content of a PDF file to ChatGPT and ask a question about its contents
    
    Args:
        pdf_text: Text content in the PDF file
        
    Returns:
        str: ChatGPT's response
    """
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Doesn't work, API deprecated in version 0.28 
    # response = openai.File.create(
    #     file=open(pdf_path, 'rb'),
    #     purpose='answers'
    # )
    # return response['id']
    
    # with open(pdf_path, 'r') as f:
    #     pdf_text = f.read()

    try:
        # Create message with PDF attachment
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Here is a markdown file containing information about an insurance policy. Please return structured output based on the fields defined in InsuranceData. The fields `forms` and `endorsements` might occur on several pages. Return all forms and endorsements mentioned in the text."
                    },
                    {
                        "type": "text",
                        "text": pdf_text,
                        # "mime_type": "text"
                    }
                ],
            }
        ]
        
        # Call ChatGPT API
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=messages,
            # max_tokens=10000,
            response_format=InsurancePolicyData
        )
        
        return response.choices[0].message.parsed
        
    except Exception as e:
        print(f"Error querying ChatGPT: {str(e)}")
        return None

def extract_structured_output(filename: str):
    """
    Extract structured output from all PDF files in a directory
    
    Args:
        data_path (str): Path to directory containing PDF files
        
    Returns:
        list: List of extracted structured data from each PDF
    """
    
    if filename.endswith('.pdf'):        
        md_text = pymupdf4llm.to_markdown(filename)
        # Extract data from each file
        result = ask_question_about_pdf(md_text)

    return result

if __name__=="__main__":
    # questions = [
    #     "What is the policy number in this document?",
    #     "What is the start and end date of this policy?",
    #     "What is the address of the insured?",
    #     "What is the total annual premium of the policy?",
    #     "Provide a list of all the forms and endorsements that make up this policy. The output format should be in pairs of form/endorsement number and corresponding description."
    # ]
    # md_text = pymupdf4llm.to_markdown("/Users/manpreet/Downloads/POL - WCOM 23-24 HRT.pdf")
    # md_text = pymupdf4llm.to_markdown("/Users/manpreet/Downloads/POL-WCOM23-24renewal$9,548-LIBMUT.pdf")
    # pathlib.Path("output.md").write_bytes(md_text.encode())

    result = ask_question_about_pdf("/Users/manpreet/Desktop/projects/pdf-agents/output1.md")
    # print(result)
    for form in result.forms_and_endorsements:
        print(form)
    # for endorsement in result.endorsements:
        # print(endorsement)
