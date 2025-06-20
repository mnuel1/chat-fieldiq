from dotenv import load_dotenv
import os
from google import genai
from google.genai import types
import re
import json
from fastapi import APIRouter

router = APIRouter()

load_dotenv()

apiKey = os.getenv("GEMINI_API_KEY")
model = "gemini-2.0-flash"

# Use the API key
client = genai.Client(api_key=apiKey)

def handle_general_questions(prompt):

  with open("prompts/ask_general_questions.txt", "r") as file:
    system_instruction_text = file.read()

  response = client.models.generate_content(
      model=model,
      config=types.GenerateContentConfig(
          system_instruction=system_instruction_text
  ),  
      contents=prompt
  )

  cleaned = re.sub(r"^```json|```$", "", response.text.strip(), flags=re.IGNORECASE).strip()

  # Convert to JSON (i.e., Python dict)
  response = json.loads(cleaned)
  print(response)
  return response
  
def handle_log_data(prompt):

  with open("prompts/ask_log_report.txt", "r") as file:
    system_instruction_text = file.read()

  response = client.models.generate_content(
      model=model,
      config=types.GenerateContentConfig(
          system_instruction=system_instruction_text
  ),  
      contents=prompt
  )

  cleaned = re.sub(r"^```json|```$", "", response.text.strip(), flags=re.IGNORECASE).strip()

  # Convert to JSON (i.e., Python dict)
  response = json.loads(cleaned)
  print(response)
  return response

def handle_requested_file(response):
  
  # Sample response
  # {
  #   'id': 4, 
  #   'confidence': 0.95, 
  #   'response': {
  #     'message': 'Narito po ang guide natin para sa pagbasa ng FCR. Sana makatulong ito!', 
  #     'file_type': 'pdf', 
  #     'subject': 'training_tips',
  #     'topic': "broiler_starter_feeding"
  #     }
  # }

  # search in db which selects the subject and topic these are predefines so no problem for flexibilty return not found if no resource available
  # for now we only have "broiler_starter_feeding" so just return that 
  # but prepare a search in db

  

  return 1

def handle_support_forms(response):

  # Sample response
  # {
  #   'id': 5, 
  #   'confidence': 0.95, 
  #   'response': {
  #     'message': 'Sige po, tutulungan namin kayo. Anong klaseng tulong ang kailangan ninyo?', 
  #     'field': 'vet_assistance'
  #     }
  # }

  # if applicable, get what vet assistance we have in database
  # if none just create pre defined org for vet assitance, technical consult and customer support(this is going to be our company)
  # other pre define fields
  #   i. "vet_assistance" – if the request involves veterinary help
  #   ii. "technical_consultation" – for feed or farm management consultation
  #   iii. "customer_support" – for general support or company contact


  return 1

# get intent of the user based from their prompt
# 3 core intents
# general question prompt
# log prompt
# requeste document prompt
def get_intent(prompt):

  with open("prompts/ask_intent.txt", "r") as file:
    system_instruction_text = file.read()

  response = client.models.generate_content(
      model=model,
      config=types.GenerateContentConfig(
          system_instruction=system_instruction_text
  ),  
      contents=prompt
  )


  # clean response
  # remove the json block to return only the json object
  cleaned = re.sub(r"^```json|```$", "", response.text.strip(), flags=re.IGNORECASE).strip()

  # Convert to JSON (i.e., Python dict)
  intent = json.loads(cleaned)

  return intent

# @router.post("/farmer/chat")
def chat_service(prompt):

  try:
    # Get intent index and perform specific action for those intents
    # 1 = general_questions
    # 2,3 = log_data
    # 4 get_requested_file
    # 5 return help support forms and details
    # 6 just return
    
    intent = get_intent(prompt)
    print(intent)

    # Early return for out of scope       
    if (intent["id"] == 6):
      return intent

  #   dispatch = {
  #     1: handle_general_questions,
  #     2: handle_log_data,
  #     3: handle_log_data,
  #     4: handle_requested_file,
  #     5: handle_support_forms,  
  #   }
  #   handler = dispatch.get(intent["id"])

  #   if (handler):
  #     return handler(prompt, intent)
  #   else:
  #     raise ValueError("Intent id cannot be found.")

  except Exception as e:
    print(f"An error occurred: {e}")


#@router.post("/farmer/logs")
def log_service():


  return 1


prompt = "Nilalagyan ko ng kalamansi at bawang yung feed para sa manok ko araw-araw. Parang lumalakas naman sila pero gusto ko malaman kung safe talaga."

# process(prompt)
handle_log_data(prompt)
