from fastapi import APIRouter

from models.chat_model import ChatRequest
from core.chat_core import Chat
from llm.salesrep_llm_handler import (
  get_intent,
  handle_general_questions,
  handle_log_data,
  handle_requested_file,
  handle_support_forms
)


router = APIRouter()


# @router.post("/salesrep/chat")
def chat_service(body: ChatRequest):
  try:
    chat = Chat()

    # chat_id = body.chat_id
    # if (chat_id == None):
    #     # create chat conversation
    #     chat_id = chat.create_conversation(body.user_id)
    #     if chat_id is None:
    #       raise Exception("Failed to create conversation")

    intent = get_intent(body.prompt)
    # intent = {
    #     "id": 7,
    #     "confidence": 0.92,
    #     "response": "Out of scope"
    # }
    # Early return for out of scope       
    # if (intent["id"] == 6):        
    #   return {"message": "Success", "data": intent}

    print(intent)
    
    # record user message
    # chat.add_message(chat_id, "user", body.prompt)

    # dispatch = {
    #   1: lambda: handle_general_questions(body.prompt),
    #   2: lambda: handle_log_data(body.prompt),
    #   3: lambda: handle_log_data(body.prompt),
    #   4: lambda: handle_requested_file(intent),
    #   5: lambda: handle_support_forms(intent),    
    # }

    # handler = dispatch.get(intent["id"])
    # if handler is None:
    #   raise Exception("Handler for intent not found")

    # return {"message": "Success", "data": handler()}
    return {"message": "Success"}
  except Exception as e:
    print(f"An error occurred: {e}")
    return {"message": "Something went wrong", "data": None}

response = handle_log_data("Farmer noticed smell in Layer 3 feed")

# Print the full response
print("Response:", response)


#@router.post("/salesrep/logs")
def log_service():
  return 1

#@router.post("/salesrep/request/collateral")
def request_collateral():
  return 1