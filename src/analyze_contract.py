import os
import json
import google.generativeai as genai
from src.config import settings


genai.configure(api_key=settings.google_api_key)

model = genai.GenerativeModel(
    "gemini-1.5-pro",
    generation_config={"response_mime_type": "application/json"}
)


async def analyze_document(file_path, prompt_text):
    sample_pdf = genai.upload_file(file_path)
    contents = [prompt_text, sample_pdf]
    raw_response = model.generate_content(contents)
    response = json.loads(raw_response.text)
    return response
