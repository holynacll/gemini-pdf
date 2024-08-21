import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel('gemini-1.5-pro')

async def analyze_document(file_path, prompt_text):
    sample_pdf = genai.upload_file(file_path)
    contents = [prompt_text, sample_pdf]
    response = model.generate_content(contents)
    return response.text