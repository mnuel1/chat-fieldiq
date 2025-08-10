import re
import json
from config.config import get_gpt_model, get_gpt_client
from core.chat_core import Chat
from core.faq_core import Faq
from core.farmer_core import Farmer
from core.salesrep_core import SalesRep

client = get_gpt_client()
gptModel = get_gpt_model()

def load_prompt(file_path):
  with open(file_path, "r", encoding="utf-8") as file:
    return file.read()

def load_functions(file_path):
  with open(file_path, "r", encoding="utf-8") as file:
    return json.load(file)

def call_openai(messages, functions, function_name):
  response = client.chat.completions.create(
    model=gptModel,
    messages=messages,
    functions=[functions],
    function_call={"name": function_name}
  )
    
  # Extract the function call arguments as JSON
  arguments = response.choices[0].message.function_call.arguments
  return json.loads(arguments)

def extract_json(text):
  match = re.search(r"```json\s*(\{.*?\})\s*```", text.strip(), re.DOTALL | re.IGNORECASE)  
  if not match:
    raise ValueError("No JSON block found in the response.")
  cleaned = match.group(1).strip()
  try:
    return json.loads(cleaned)
  except json.JSONDecodeError:
    raise ValueError(f"Invalid JSON response: {cleaned}")

def store_message_faq(chat_id, prompt, response, category, metadata=None):
  chat = Chat()
  faq = Faq()
  chat.add_message(chat_id, "user", prompt, metadata)
  chat.add_message(chat_id, "model", response, metadata)
  faq.insert_faq(prompt, response, category)

def handle_log(chat_id, user_id, prompt, prompt_file, form_key, function_name, on_complete):
  chat = Chat()
  farmer = Farmer()

  system_instruction = load_prompt(f"{prompt_file}.txt")
  functions = load_functions(f"{prompt_file}.json")

  convo_res = chat.get_conversations_record(chat_id)
  form_data = convo_res.get("form_data") or {}
  print(chat_id)
  print(get_max_messages())
  chat_history = chat.get_recent_messages(chat_id, get_max_messages())
  print(chat_id)
  print(get_max_messages())
  form_summary = "\n".join([f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in form_data.items() if v]) or "None yet"

  chat_history.append({
    "role": "user",
    "content": f"{prompt}\n\n(Previously collected info):\n{form_summary}"
  })

  messages = [{"role": "system", "content": system_instruction}] + chat_history
  # response_text = call_openai(messages)
  parsed = call_openai(messages, functions, function_name)

  if form_key != "": 
    new_fields = parsed.get(form_key, {})
    form_data.update({k: v for k, v in new_fields.items() if v})
    
    chat.update_conversation(chat_id, form_data=form_data)
    
    if parsed["next_action"] == "log_complete":
      on_complete(farmer, user_id, form_data, parsed)
      chat.update_conversation(chat_id, None)

  store_message_faq(chat_id, prompt, parsed["response"], parsed["log_type"],
                    metadata={"form_data": form_data, "next_action": parsed["next_action"]})
  return parsed

def handle_log_sales(chat_id, user_id, prompt, prompt_file, form_key, function_name, on_complete):
  chat = Chat()
  salesrep = SalesRep()
  
  system_instruction = load_prompt(f"{prompt_file}.txt")
  functions = load_functions(f"{prompt_file}.json")

  convo_res = chat.get_conversations_record(chat_id)
  form_data = convo_res.get("form_data") or {}

  chat_history = chat.get_recent_messages(chat_id, get_max_messages())
  form_summary = "\n".join([f"{k.replace('_', ' ').capitalize()}: {v}"for k, v in form_data.items() if v]) or "None yet"

  chat_history.append({
    "role": "user",
    "content": f"{prompt}\n\n(Previously collected info):\n{form_summary}"
  })
  messages = [{"role": "system", "content": system_instruction}] + chat_history
  # response_text = call_openai(messages)
  parsed = call_openai(messages, functions, function_name)

  new_fields = parsed.get(form_key, {})
  form_data.update({k: v for k, v in new_fields.items() if v})
  
  chat.update_conversation(chat_id, form_data=form_data)
  store_message_faq(chat_id, prompt, parsed["response"], parsed["log_type"],
                    metadata={"form_data": form_data, "next_action": parsed["next_action"]})
  
  if parsed["next_action"] == "log_complete":
    on_complete(salesrep, user_id, form_data, parsed)
    chat.update_conversation(chat_id, None)
    

  return parsed

def handle_intent(prompt, prompt_file, function_name):
  system_instruction = load_prompt(f"{prompt_file}.txt")
  functions = load_functions(f"{prompt_file}.json")
  messages = [
    {"role": "system", "content": system_instruction},
    {"role": "user", "content": prompt}
  ]
  parsed = call_openai(messages, functions, function_name)
  return parsed

def get_max_messages():
  return 6