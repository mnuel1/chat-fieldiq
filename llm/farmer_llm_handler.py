from core.chat_core import Chat
from core.farmer_core import Farmer
from core.helper_core import load_prompt, call_openai, extract_json, store_message_faq, get_max_messages, handle_log, handle_intent, load_functions

max = get_max_messages()

def handle_general_questions(chat_id, user_id, prompt):
  chat = Chat()
  farmer = Farmer()

  system_instruction = load_prompt("prompts/ask_farmer_general_questions.txt")
  functions = load_functions("prompts/ask_farmer_general_questions.json")
  days_on_feed, current_feed = farmer.get_feed_use(user_id)

  history = chat.get_recent_messages(chat_id, max_messages=max)
  history.append({
    "role": "user",
    "content": f"{prompt}\n\nDays on feed: {days_on_feed}\nCurrent feed: {current_feed}"
  })

  messages = [{"role": "system", "content": system_instruction}] + history

#   response_text = call_openai(messages)
  parsed = call_openai(messages, functions, "feed_advisory")

  store_message_faq(chat_id, prompt, parsed["response"], parsed["log_type"])
  return parsed

def handle_health_log(chat_id, user_id, prompt):
  return handle_log(
    chat_id, 
    user_id, 
    prompt, 
    "prompts/ask_farmer_health_log", 
    "incident_details",
    "log_health_incident",
    lambda farmer, user_id, form_data, parsed: farmer.create_health_incident(
        user_id, form_data
    ))

def handle_general_log(chat_id, user_id, prompt):
  return handle_log(
    chat_id, 
    user_id, 
    prompt, 
    "prompts/ask_farmer_log",
    "report_details",
    "log_performance_report",
    lambda farmer, user_id, form_data, parsed: farmer.create_health_incident(
        user_id, form_data
    )
  )

def handle_local_practice_log(chat_id, user_id, prompt):
  return handle_log(
    chat_id, 
    user_id, 
    prompt, 
    "prompts/ask_farmer_diy_log", 
    "",
    "log_diy_practice",
    lambda farmer, user_id, form_data, parsed: farmer.create_health_incident(
        user_id, form_data
    ))
    

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

    return {
      'id': 4,
      'confidence': 0.95,
      'response': {
        'message': 'Narito po ang guide natin para sa pagbasa ng FCR. Sana makatulong ito!',
        'file_type': 'pdf',
        'subject': 'training_tips',
        'topic': "broiler_starter_feeding"
        }
    }

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

    return {
      'id': 5,
      'confidence': 0.95,
      'response': {
        'message': 'Sige po, tutulungan namin kayo. Anong klaseng tulong ang kailangan ninyo?',
        'field': 'vet_assistance'
        }
    }

def get_intent(prompt, prompt_file, function_name):
    return handle_intent(prompt, prompt_file, function_name)