from google.genai import types
import re
import json

from config.config import get_gemini_client, get_llm_model
from core.chat_core import Chat
from core.faq_core import Faq
from core.farmer_core import Farmer

model = get_llm_model()
client = get_gemini_client()


def store_message_faq(chat_id, prompt, response, category, metadata = None):
    chat = Chat()
    faq = Faq()

    # record user message
    chat.add_message(chat_id, "user", prompt, metadata)
    chat.add_message(chat_id, "model", response, metadata)

    # record faq
    faq.insert_faq(prompt, response, category)

def handle_general_questions(chat_id, user_id, prompt):

    chat = Chat()
    farmer = Farmer()

    with open("prompts/ask_farmer_general_questions.txt", "r", encoding='utf-8') as file:
        system_instruction_text = file.read()

    days_on_feed, current_feed = farmer.get_feed_use(user_id)

    history = chat.get_recent_messages(chat_id, max_messages=10)

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

    cleaned = re.sub(r"^```json|```$", "", response.text.strip(),
                     flags=re.IGNORECASE).strip()

    # Convert to JSON (i.e., Python dict)
    response = json.loads(cleaned)

    store_message_faq(chat_id, prompt, response["response"], response["log_type"])

    return response

def handle_health_log(chat_id, user_id, prompt):    
    with open("prompts/ask_farmer_health_log.txt", "r", encoding='utf-8') as file:
        system_instruction = file.read()
  
    chat = Chat()
    farmer = Farmer()

    # Get the form data value from farmer chat_conversation record
    convo_res = chat.get_conversations_record(chat_id)
    form_data = convo_res.get("form_data") or {}

    # Get recent chat message history limit to 10 or kung ilan anong mas optimal at accurate
    chat_history = chat.get_recent_messages(chat_id, 10)

    # Form summary para ma track ni gemini yung mga nasagot na sa form for health incident
    form_summary = "\n".join([
        f"{k.replace('_', ' ').capitalize()}: {v}"
        for k, v in form_data.items() if v
    ]) or "None yet"

    # Latest prompt + form summary...
    chat_history.append({
        "role": "user",
        "parts": [
            {"text": f"{prompt}\n\n(Previously collected info):\n{form_summary}"}
        ]
    })

    # Feed gemini with the chat history and system instruction and latest prompt
    response = client.models.generate_content(
        model=model,
        config={"system_instruction": system_instruction},
        contents=chat_history
    )
    
    match = re.search(r"```json\s*(\{.*?\})\s*```",
                      response.text.strip(), re.DOTALL)
    if not match:
        raise ValueError("No JSON block found in the response.")
    json_str = match.group(1)
    parsed = json.loads(json_str)

    # Merge new fields from Gemini into form_data
    new_fields = parsed.get("incident_details", {})
    form_data.update({k: v for k, v in new_fields.items()
                     if v is not None and v != ""})

    # Save updated form_data to chat_conversations
    status = "active" if parsed["next_action"] != "log_complete" else "completed"
    chat.update_conversation(
        chat_id, form_data=form_data)

    # Save yung latest user prompt and model response
    store_message_faq(chat_id, prompt, parsed["response"], parsed["log_type"], metadata={"form_data": form_data, "next_action": parsed["next_action"]})
   
    # Final submission to health_incidents table pag yung form_data sa chat_conversation na filled na lahat
    if parsed["next_action"] == "log_complete":
        farmer.create_health_incident(
            farmer_user_profile_id=user_id,
            form_data=form_data
        )
        chat.update_conversation(chat_id, None)

    return parsed

def handle_local_practice_log(chat_id, user_id, prompt):

    with open("prompts/ask_farmer_diy_log.txt", "r", encoding='utf-8') as file:
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

    store_message_faq(chat_id, prompt, response["response"], response["log_type"])

    return response

def handle_general_log(chat_id, user_id, prompt):
    with open("prompts/ask_farmer_log.txt", "r", encoding='utf-8') as file:
        system_instruction = file.read()
  
    chat = Chat()
    farmer = Farmer()

    # Get the form data value from farmer chat_conversation record
    convo_res = chat.get_conversations_record(chat_id)
    form_data = convo_res.get("form_data") or {}

    # Get recent chat message history limit to 10 or kung ilan anong mas optimal at accurate
    chat_history = chat.get_recent_messages(chat_id, 10)

    # Form summary para ma track ni gemini yung mga nasagot na sa form for health incident
    form_summary = "\n".join([
        f"{k.replace('_', ' ').capitalize()}: {v}"
        for k, v in form_data.items() if v
    ]) or "None yet"

    # Latest prompt + form summary...
    chat_history.append({
        "role": "user",
        "parts": [
            {"text": f"{prompt}\n\n(Previously collected info):\n{form_summary}"}
        ]
    })

    # Feed gemini with the chat history and system instruction and latest prompt
    response = client.models.generate_content(
        model=model,
        config={"system_instruction": system_instruction},
        contents=chat_history
    )
    
    match = re.search(r"```json\s*(\{.*?\})\s*```",
                      response.text.strip(), re.DOTALL)
    if not match:
        raise ValueError("No JSON block found in the response.")
    json_str = match.group(1)
    parsed = json.loads(json_str)

    # Merge new fields from Gemini into form_data
    new_fields = parsed.get("incident_details", {})
    form_data.update({k: v for k, v in new_fields.items()
                     if v is not None and v != ""})

    # Save updated form_data to chat_conversations
    status = "active" if parsed["next_action"] != "log_complete" else "completed"
    chat.update_conversation(
        chat_id, form_data=form_data)

    # Save yung latest user prompt and model response
    store_message_faq(chat_id, prompt, parsed["response"], parsed["log_type"], metadata={"form_data": form_data, "next_action": parsed["next_action"]})
   
    # Final submission to health_incidents table pag yung form_data sa chat_conversation na filled na lahat
    if parsed["next_action"] == "log_complete":
        # farmer.create_health_incident(
        #     farmer_user_profile_id=user_id,
        #     form_data=form_data
        # )
        chat.update_conversation(chat_id, None)

    return parsed

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

    # clean response
    # remove the json block to return only the json object
    cleaned = re.sub(r"^```json|```$", "", response.text.strip(),
                     flags=re.IGNORECASE).strip()

    # Convert to JSON (i.e., Python dict)
    intent = json.loads(cleaned)

    return intent
