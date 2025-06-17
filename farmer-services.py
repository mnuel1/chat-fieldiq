from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
import re
import json

load_dotenv()

apiKey = os.getenv("GEMINI_API_KEY")
model = "gemini-2.0-flash"

# Use the API key
client = genai.Client(api_key=apiKey)


def general_questions(intent):

  response = client.models.generate_content(
      model=model,
      config=types.GenerateContentConfig(
          system_instruction=""
  ),  
      contents=intent
  )

  return response

def log_data(intent):

  response = client.models.generate_content(
      model=model,
      config=types.GenerateContentConfig(
          system_instruction=""
  ),  
      contents=intent
  )

  return response

def get_requested_file(intent):
  
  file = "/path/here/file1.pdf"

  return file


def get_intent(prompt):
  # get intent
  response = client.models.generate_content(
      model=model,
      config=types.GenerateContentConfig(
          system_instruction="" \
          "You are an intent classifier for a smart farming assistant that supports Filipino farmers. " \
          "1. Ask Product/Feed Questions/Guidance" \
          "2. Log Farm Performance  " \
          "3. Report Health Issues" \
          "4. Download Feeding Guides" \
          "5. Request Training / Tips" \
          "6. Share Local Practices / Ask If Safe" \
          "7. Request Help from a Vet or Support Team" \
          "8. Out of Scope (if not related to agriculture or other brand/competitors mentioned. Do not promote/compare brands)" \
          "Understand the input in English, Tagalog, Bisaya, or any Filipino dialect. " \
          "If the intent is out of scope respond in a neutral manner (put it in note and respond in taglish and make it natural)" \
          "Respond only with a clean JSON." \
          "Example Output:" \
          "{" \
          "intent: [Log Farm Performance]," \
          "confidence: [0.92]" \
          "notes: [Mentions FCR and weight logging]" \
          "}" 
          


  ),  
      contents=prompt
  )  

  cleaned = re.sub(r"^```json|```$", "", response.text.strip(), flags=re.IGNORECASE).strip()

  # Convert to JSON (i.e., Python dict)
  intent = json.loads(cleaned)

  return intent
  
def process(prompt):
  
  intent = get_intent(prompt)

  print(intent["intent"])

input = "Anong feed ang pang-28 days?"
process(input)
