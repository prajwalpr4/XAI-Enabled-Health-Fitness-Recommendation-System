"""
List available Gemini models
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
    print("Available models:")
    for model in genai.list_models():
        print(f"- {model.name}")
else:
    print("GOOGLE_API_KEY not found in .env file")
