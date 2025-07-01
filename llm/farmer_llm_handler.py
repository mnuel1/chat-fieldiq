from google.genai import types
import re
import json

from config.config import get_gemini_client, get_llm_model
from core.chat_core import Chat
from core.faq_core import Faq
from core.farmer_core import Farmer

model = get_llm_model()
client = get_gemini_client()

def store_message_faq(chat_id, prompt, response, category): 
  chat = Chat()
  faq = Faq()

  # record user message
  chat.add_message(chat_id, "user", prompt)
  chat.add_message(chat_id, "model", response)

  # record faq
  faq.insert_faq(prompt, response, category)


def handle_general_questions(chat_id, user_id, prompt):
  
  chat = Chat()
  farmer = Farmer()

  with open("prompts/ask_general_questions.txt", "r") as file:
    system_instruction_text = file.read()

  days_on_feed, current_feed = farmer.get_feed_use(user_id)

  history = chat.get_recent_messages(chat_id, max_messages=6)

   # Append the current prompt as a user message
  history.append({
      "role": "user",
      "parts": [
          {"text": f"{prompt}\n\nDays on feed: {days_on_feed}\nCurrent feed: {current_feed}"}
      ]
  })

  # Make the request to the model
  response = client.models.generate_content(
      model=model,
      config=types.GenerateContentConfig(
          system_instruction=system_instruction_text
      ),
      contents=history
  )

  print(response.text)

  cleaned = re.sub(r"^```json|```$", "", response.text.strip(), flags=re.IGNORECASE).strip()

  # Convert to JSON (i.e., Python dict)
  response = json.loads(cleaned)

  store_message_faq(chat_id, prompt, response["response"], response["log_type"])
  
  return response


def handle_log_data(chat_id, user_id, prompt):
  
  with open("prompts/ask_farmer_log_report.txt", "r") as file:
    system_instruction_text = file.read()

  response = client.models.generate_content(
      model=model,
      config=types.GenerateContentConfig(
          system_instruction=system_instruction_text
  ),  
      contents=prompt
  )

  print(response.text)

  cleaned = re.sub(r"^```json|```$", "", response.text.strip(), flags=re.IGNORECASE).strip()

  # Convert to JSON (i.e., Python dict)
  response = json.loads(cleaned)

  store_message_faq(chat_id, prompt, response["response"], response["log_type"])

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

def get_intent(prompt):

  with open("prompts/ask_farmer_intent.txt", "r") as file:
    system_instruction_text = file.read()

  response = client.models.generate_content(
      model=model,
      config=types.GenerateContentConfig(
          system_instruction=system_instruction_text
  ),  
      contents=prompt
  )

  print(response.text)
  # clean response
  # remove the json block to return only the json object
  cleaned = re.sub(r"^```json|```$", "", response.text.strip(), flags=re.IGNORECASE).strip()

  # Convert to JSON (i.e., Python dict)
  intent = json.loads(cleaned)

  return intent
