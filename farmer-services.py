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

# get intent of the user based from their prompt
# 3 core intents
# general question prompt
# log prompt
# requeste document prompt

def get_intent(prompt):
  
  
  response = client.models.generate_content(
      model=model,
      config=types.GenerateContentConfig(
          system_instruction="" \
          "You are an intent classifier for a smart farming assistant that supports Filipino farmers. " \
          "Use the intents below and refer to description."
          "Intent - Description"
          "1. Ask Product or Feed Questions or Guidance - When the farmer ask questions about feeding programs, timing, types of feed, mixing practices, effects on poultry performance, and feed form (pellets vs crumble), etc" \
          "2. Report Health Issues - When the farmer reports sickness, death, or abnormal behavior in flocks for logging or advice (e.g., 'may namatay', 'hindi kumakain', 'lima ang namatay')" \
          "3. Share Local Practices or Ask If Safe - When the farmer share DIY, local practices or ask if those practices/DIY are safe" \
          "4. Download Guide or Request Training Content - When the farmer request downloadable guides, videos, or training materials." \
          "5. Request Help Vet or Support Team - When the farmer is actively asking for help, check-up, consultation, or expert opinion (e.g., 'pwede bang may tumingin', 'kailangan ng tulong', 'patingin vet')" \
          "6. Out of Scope - if not related to agriculture or other brand/competitors mentioned. Do not promote/compare brands" \
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


  # clean response
  # remove the json block to return only the json object
  cleaned = re.sub(r"^```json|```$", "", response.text.strip(), flags=re.IGNORECASE).strip()

  # Convert to JSON (i.e., Python dict)
  intent = json.loads(cleaned)

  return intent
  
def process(prompt):
  
  intent = get_intent(prompt)

  print(intent["intent"])

input = "Today is weight is 1.6kg?" 
process(input)
