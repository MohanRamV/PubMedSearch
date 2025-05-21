# src/llm_utils.py

import os
import re
from dotenv import load_dotenv
import streamlit as st
from src.prompt_templates import CATEGORIZATION_PROMPT
from src.utils import safe_parse_llm_response
import json
import google.generativeai as genai
from src.prompt_templates import EMBASE_QUERY_PROMPT

# Load API keys from .env
load_dotenv()
GEMINI_API_KEY = st.secrets["GOOGLE_API_KEY"]



# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")



#Embase query generation
def generate_embase_query(user_query: str) -> str:
    """
    Uses LLM to generate an Embase-compatible Boolean query from user input.
    """
    prompt = EMBASE_QUERY_PROMPT.format(query=user_query)
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Embase LLM generation error: {e}")
        return ""

def categorize_user_query(user_query: str) -> str:
    prompt = CATEGORIZATION_PROMPT.format(query=user_query)

    try:
        response = model.generate_content(prompt)
        print("🔎 Raw Gemini response:\n", response.text)
        return response.text.strip()  # No longer JSON
    except Exception as e:
        print(f"❌ LLM categorization error: {e}")
        return ""

    
def refine_user_query(user_query: str, failed_results: list) -> str:
    """
    Uses LLM to rewrite a user query for better PubMed search results.
    """
    prompt = f"""
    The following PubMed query returned few or irrelevant results:

    User Query: "{user_query}"
    Sample Returned Titles:
    {', '.join([r.get('title', '') for r in failed_results[:3]])}

    Suggest an improved biomedical search query that might return more relevant results.
    Keep it concise and medically accurate.
    """

    # Replace with your LLM (Gemini/GPT) call:
    response = model.generate_content(prompt)
    return response.text.strip()
