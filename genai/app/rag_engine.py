from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import json
import random
from google import genai
from google.genai import types

from typing import List, Tuple
from app.models import TarotCard
from app.prompt_loader import load_tarot_template, render_prompt


load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def check_environment_variables():
    if not API_KEY :
        raise RuntimeError("Missing GEMINI_API_KEY in environment")
    
def build_tarot_prompt(question: str, picks):
    template_str = load_tarot_template()  
    return render_prompt(template_str, question, picks)

def call_gemini_api(prompt: str) -> str:
    """
    Call the Gemini API with the provided prompt and return the response.
    """
    check_environment_variables()
    # Load the configuration from the JSON file
    with open(os.path.join(os.path.dirname(__file__), "gemini_config.json"), "r", encoding="utf-8") as f:
        cfg = json.load(f)

    gen_cfg = types.GenerationConfig(**cfg["generation_config"])
    safe_cfg = [types.SafetySetting(**s) for s in cfg["safety_settings"]]

    gen_cfg = types.GenerateContentConfig(
        **cfg["generation_config"],
        safety_settings=safe_cfg,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )

    client = genai.Client(api_key = API_KEY)
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-04-17",
        contents=prompt,
        config=gen_cfg
    )
    # print("Response:", response.text)
    return response.text 

def store_feedback(user_id: str, question: str, feedback: str) -> None:
    # Placeholder for storing feedback
    pass

