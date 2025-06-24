from fastapi import APIRouter
from llm.farmer_llm_handler import (
  get_intent,
  handle_general_questions,
  handle_log_data,
  handle_requested_file,
  handle_support_forms
)

router = APIRouter()


# @router.post("/farmer/chat")
def chat_service(prompt, user_id, chat_id=None):
    try:
        # Get intent index and perform specific action for those intents
        # 1 = general_questions
        # 2,3 = log_data
        # 4 get_requested_file
        # 5 return help support forms and details
        # 6 just return

        if (chat_id != None):
            # create chat conversation
            print("created")
        
        intent = get_intent(prompt)
        
        # Early return for out of scope       
        if (intent["id"] == 6):
            # record_message()
            print("recorded")

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