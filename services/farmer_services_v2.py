
from fastapi import APIRouter, HTTPException

from core.chat_core import Chat
from core.farmer_core_v2 import FarmerV2
from exceptions.global_exception import GlobalException
from llm.farmer_llm_handler import get_intent, handle_general_log, handle_general_questions, handle_health_log, handle_local_practice_log, handle_requested_file, handle_support_forms
from models.chat_model import ChatRequest
from models.feed_calculator_model import CreateFeedCalculatorPayload, FeedCalculationResponse, FeedCalculatorDto, UpdateFeedCalculatorPayload
from models.feed_programs_model import FeedProgramPayload


router = APIRouter()

@router.post("/chat-ai")
def chat_service(body: ChatRequest):
    try:
        chat = Chat()

        chat_id = body.chat_id
        user_id = body.user_id
        prompt = body.prompt
        
        chat_id = chat.create_conversation(user_id)
        
        if chat_id == None:
            raise Exception("Failed to create conversation")
            
        intent_id = body.intent_id
        intent = {}
        if (intent_id == None or intent_id == 0):
            intent = get_intent(prompt, "prompts/ask_farmer_intent", "classify_intent")  
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

# Create feed program
@router.post("/feed-programs")
def create_feed_program(payload: FeedProgramPayload):
  try:
    farmer = FarmerV2()
    
    result = farmer.create_feed_program(
      payload.farmer_user_profile_id,
      payload.feed_product_id
    )
    return {"message": "Success", "data": result}
  except Exception as e:
    print(f"An error occured: {e}")
    raise HTTPException(status_code=500, detail="Failed to create feed program.")
  
  
# Get current active feed program
@router.get("/feed-programs/farmer-user-profile/{id}/active")
def get_active_feed_program(id: int):
    try:
        farmer = FarmerV2()
        result = farmer.get_active_feed_program(id)
        return {"message": "Success", "data": result}

    except GlobalException as ge:
        raise HTTPException(status_code=ge.status_code, detail=str(ge))

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to get active feed program.")
    
@router.get("/feed-programs/farmer-user-profile/{id}/feed-product/active")
def get_active_feed_product(id: int):
    try:
        farmer = FarmerV2()
        result = farmer.get_active_feed_product(id)
        return {"message": "Success", "data": result}
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to get active feed program.")
      

@router.put("/feed-programs/farmer-user-profile/{id}/complete")
def complete_active_feed_program(id: int):
    try:
        farmer = FarmerV2()
        result = farmer.complete_active_feed_program(id)

        if not result:
            raise HTTPException(status_code=404, detail="No active feed program to complete.")

        return {"message": "Success", "data": {"feed_program_id": result, "status": "completed"}}

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to complete feed program.")


@router.put("/feed-programs/farmer-user-profile/{id}/incomplete")
def incomplete_active_feed_program(id: int):
    try:
        farmer = FarmerV2()
        result = farmer.incomplete_active_feed_program(id)

        if not result:
            raise HTTPException(status_code=404, detail="No active feed program to mark as incomplete.")

        return {"message": "Success", "data": {"feed_program_id": result, "status": "incomplete"}}

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark feed program as incomplete.")
    
@router.post("/feed-calculation-log")
def create_feed_calculation_log(payload: CreateFeedCalculatorPayload):
    try:
        farmer = FarmerV2()
        result = farmer.create_feed_calculation_log(
            user_profile_id=payload.user_profile_id,
            log_data=payload.log_data
        )
        return {"message": "Success", "data": result}
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to create feed calculation log")
        
@router.get("/feed-calculation-log/farmer-user-profile/{id}", response_model=FeedCalculationResponse)
def get_feed_calculation_log(id: int):
    try:
        farmer = FarmerV2()
        result = farmer.read_feed_calculation_log(id)
        
        return {"message": "Success", "data": result}
    
    except GlobalException as ge:
        raise HTTPException(status_code=ge.status_code, detail=str(ge))

    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to get feed calculation log")


@router.put("/feed-calculation-log/farmer-user-profile/{id}")
def update_feed_calculation_log(id: int, payload: UpdateFeedCalculatorPayload):
    try:
        farmer = FarmerV2()
        result = farmer.update_feed_calculation_log(id, payload)
        if not result:
            raise HTTPException(
                status_code=404, detail="Feed calculation log not found")
        return {"message": "Success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to update feed calculation log")

@router.get("/growth-performance/farmer-user-profile/{id}")
def get_growth_performance(id: int):
    try:
        farmer = FarmerV2()
        result = farmer.read_growth_performance(id)
        return {"message": "Success", "data": result}
    
    except GlobalException as ge:
        raise HTTPException(status_code=ge.status_code, detail=str(ge))
    
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="Failed to get growth performance data.")

    
