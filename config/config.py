from supabase import create_client, Client
from google import genai
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
model = "gemini-2.0-flash"
gpt_model = "gpt-4.1-mini"

def get_supabase_client() -> Client:
  return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_gemini_client():
  return genai.Client(api_key=GEMINI_KEY)

def get_llm_model():
  return model

def get_gpt_client():
  return OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")
  )

def get_gpt_model():
  return gpt_model