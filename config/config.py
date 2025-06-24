from supabase import create_client, Client
from google import genai

import os
from dotenv import load_dotenv
load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
model = "gemini-2.0-flash"

def get_supabase_client() -> Client:
  return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_gemini_client():
  return genai.Client(api_key=GEMINI_KEY)

def get_llm_model():
  return model