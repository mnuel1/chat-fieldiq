from fastapi import APIRouter

from models.chat_model import ChatRequest
from core.chat_core import Chat
from llm.farmer_llm_handler import (
  get_intent,
  handle_general_questions,
  handle_log_data,
  handle_requested_file,
  handle_support_forms
)


router = APIRouter()


@router.post("/chat")
def chat_service(body: ChatRequest):
  try:
    chat = Chat()
    # Get intent index and perform specific action for those intents
    # 1 = general_questions
    # 2,3 = log_data
    # 4 get_requested_file
    # 5 return help support forms and details
    # 6 just return

    chat_id = body.chat_id
    if (chat_id == None):
      # create chat conversation
      chat_id = chat.create_conversation(body.user_id)
      if chat_id is None:
        raise Exception("Failed to create conversation")

    intent = get_intent(body.prompt)
  
    # Early return for out of scope       
    if (intent["id"] == 6):        
      return {"message": "Success", "data": intent}
    
    # record user message
    chat.add_message(chat_id, "user", body.prompt)

    dispatch = {
      1: lambda: handle_general_questions(chat_id, body.prompt),
      2: lambda: handle_log_data(chat_id, body.prompt),
      3: lambda: handle_log_data(chat_id, body.prompt),
      4: lambda: handle_requested_file(intent),
      5: lambda: handle_support_forms(intent),
    }

    handler = dispatch.get(intent["id"])
    if handler is None:
      raise Exception("Handler for intent not found")

    return {"message": "Success", "data": handler()}

  except Exception as e:
    print(f"An error occurred: {e}")
    return {"message": "Something went wrong", "data": None}

#@router.post("/logs")
def log_service():
    return 1