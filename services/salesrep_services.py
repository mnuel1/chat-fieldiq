from fastapi import APIRouter

from models.chat_model import ChatRequest
from core.chat_core import Chat
from llm.salesrep_llm_handler import (
  get_intent,
  handle_general_questions,
  handle_field_product_log,
  handle_dealer_log,
  handle_requested_file,
  handle_support_forms
)


router = APIRouter()

@router.post("/salesrep/chat")
def chat_service(body: ChatRequest):
  try:
    chat = Chat()

    chat_id = body.chat_id
    user_id = body.user_id
    
    if (chat_id == None or chat_id == 0):
        # create chat conversation
        chat_id = chat.create_conversation(body.user_id)
        if chat_id is None:
          raise Exception("Failed to create conversation")
        
    intent_id = body.intent_id
    intent = {}
    if (intent_id == None or intent_id == 0):
      intent = get_intent(body.prompt)    
      intent_id = intent["id"]

    # Early return for out of scope       
    if (intent_id == 6):        
      return {"message": "Success", "data": intent}
  
    dispatch = {
      1: lambda: handle_general_questions(chat_id, body.prompt),
      2: lambda: handle_dealer_log(chat_id, user_id, body.prompt),
      3: lambda: handle_field_product_log(chat_id, user_id, body.prompt),
      4: lambda: handle_requested_file(intent),
      5: lambda: handle_support_forms(intent),    
    }

    handler = dispatch.get(intent_id)
    if handler is None:
      raise Exception("Handler for intent not found")

    return {"message": "Success", "data": handler()}    
  except Exception as e:
    print(f"An error occurred: {e}")
    return {"message": "Something went wrong", "data": None}

#@router.post("/salesrep/logs")
def log_service():
  return 1

#@router.post("/salesrep/request/collateral")
def request_collateral():
  return 1