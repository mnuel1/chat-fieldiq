

from core.helper_core import load_prompt, call_openai, extract_json, store_message_faq, get_max_messages, handle_log_sales, handle_intent
from core.chat_core import Chat

max = get_max_messages()

def handle_general_questions(chat_id, prompt):
  
  chat = Chat()

  system_instruction = load_prompt("prompts/ask_sales_rep_general_questions.txt")
  
  history = chat.get_recent_messages(chat_id, max_messages=max)
  history.append({
    "role": "user",
    "content": prompt
  })

  messages = [{"role": "system", "content": system_instruction}] + history
  response_text = call_openai(messages)
  parsed = extract_json(response_text)

  store_message_faq(chat_id, prompt, parsed["response"], parsed["log_type"])
  return parsed

  
def handle_field_product_log(chat_id, user_id, prompt):
  return handle_log_sales(
    chat_id,
    user_id,
    prompt,
    "prompts/ask_salesrep_product_field_log",
    "incident_details",
    "log_feed_issue",
    lambda salesrep, user_id, form_data, parsed: salesrep.create_field_product_incident(
      user_id, form_data, parsed["tag"]
    )
  )
def handle_dealer_log(chat_id, user_id, prompt):
  return handle_log_sales(
    chat_id,
    user_id,
    prompt,
    "prompts/ask_salesrep_dealer_log",
    "incident_details",
    "log_dealer_issue",
    lambda salesrep, user_id, form_data, parsed: salesrep.create_dealer_incident(
      user_id, form_data, parsed["tag"]
    )
  )

def handle_sales_log(chat_id, user_id, prompt):
  return handle_log_sales(
    chat_id,
    user_id,
    prompt,
    "prompts/ask_salesrep_sales_log",
    "sales_details",
    "log_sales_activity",
    lambda salesrep, user_id, form_data, parsed: salesrep.create_sales_report(
      user_id, form_data
    )
  )

def handle_farm_log(chat_id, user_id, prompt):
  def on_farm_complete(salesrep, user_id, form_data, parsed):
    visit_details = parsed["visit_details"]
    visit_type = visit_details["visit_type"]
    ticket_number = visit_details.get("ticket_number")

    if visit_type == "planned_visit" and not ticket_number:
      ticket_number = salesrep.generate_ticket_number(user_id)
      visit_details["ticket_number"] = ticket_number
      salesrep.create_visit_report(user_id, form_data)

    elif visit_type == "completed_visit" and ticket_number:
      if salesrep.check_ticket_number_validity(ticket_number, user_id):
        salesrep.update_visit_report(ticket_number, user_id, form_data)

  return handle_log_sales(
      chat_id,
      user_id,
      prompt,
      "prompts/ask_salesrep_farm_log",
      "visit_details",
      "log_farm_visit",
      on_farm_complete
  )
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

def get_intent(prompt, prompt_file, function_name):
  return handle_intent(prompt, prompt_file, function_name)

