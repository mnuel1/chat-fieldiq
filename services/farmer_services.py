from fastapi import APIRouter

from models.chat_model import ChatRequest
from core.chat_core import Chat
from llm.farmer_llm_handler import (
  get_intent,
  handle_general_questions,
  handle_health_log,
  handle_local_practice_log,
  handle_requested_file,
  handle_support_forms,
  handle_general_log
)

router = APIRouter()

@router.post("/chat")
def chat_service(body: ChatRequest):
  try:
    chat = Chat()
      
    chat_id = body.chat_id
    user_id = body.user_id
    prompt = body.prompt

    if (chat_id == None or chat_id == 0):
      # create chat conversation
      chat_id = chat.create_conversation(user_id)
      if chat_id == None:
        raise Exception("Failed to create conversation")
    
    intent_id = body.intent_id
    intent = {}
    if (intent_id == None or intent_id == 0):
      intent = get_intent(prompt)  
      intent_id = intent["id"]

    # Early return for out of scope       
    if (intent_id == 6): 
      return {"message": "Success", "data": intent}
    
    dispatch = {
      1: lambda: handle_general_questions(chat_id, user_id, prompt),
      2: lambda: handle_health_log(chat_id, user_id, prompt),
      3: lambda: handle_local_practice_log(chat_id, user_id, prompt),
      4: lambda: handle_requested_file(intent),
      5: lambda: handle_support_forms(intent),
      7: lambda: handle_general_log(chat_id, user_id, prompt)
    }

    handler = dispatch.get(intent_id)
    if handler is None:
      raise Exception("Handler for intent not found")

    return {"message": "Success", "data": handler()}

  except Exception as e:
    print(f"An error occurred: {e}")
    return {"message": "Something went wrong", "data": None}
  


# history not working properly
# ano ang pinapakain sa 5 months
# ilang beses ito pinapakain