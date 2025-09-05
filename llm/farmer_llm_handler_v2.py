from core.chat_core import Chat
from core.company_core import Company
from core.farmer_core_v2 import FarmerV2, create_health_incident_with_program, create_performance_log_with_program
from core.helper_core_v2 import call_openai, get_feed_program_context, get_max_messages, handle_intent, handle_log, load_functions, load_prompt, store_message_faq, detect_language


max = get_max_messages()

# intent 1 ito
def handle_general_questions(chat_id, user_id, prompt):
    chat = Chat()
    farmer = FarmerV2()
    company = Company()
    
    # Get user company ID
    user_company_id = company.get_user_company(user_id)

    system_instruction = load_prompt("prompts/ask_farmer_general_questions.txt")
    functions = load_functions("prompts/ask_farmer_general_questions.json")

    # Get active feed program context
    feed_program_context = get_feed_program_context(farmer, user_id)
    
    history = chat.get_recent_messages(chat_id, max_messages=max)
    history.append({
        "role": "user",
        "content": f"{prompt}\n\n{feed_program_context}"
    })

    detected_language = detect_language(prompt)

    messages = [{
        "role": "system", 
        "content": system_instruction + f" Strictly follow this language: {detected_language} when responding."
    }] + history


    parsed = call_openai(messages, functions, "feed_advisory")

    store_message_faq(chat_id, prompt, parsed["response"], parsed["log_type"], user_company_id)
    return parsed

# intent 2 ito
def handle_health_log(chat_id, user_id, prompt):
    return handle_log(
        chat_id, 
        user_id, 
        prompt, 
        "prompts/ask_farmer_health_log", 
        "incident_details",
        "log_health_incident",
        create_health_incident_with_program)

# intent 3 ito
def handle_performance_log(chat_id, user_id, prompt):
    return handle_log(
        chat_id, 
        user_id, 
        prompt, 
        "prompts/ask_farmer_log",
        "report_details",
        "log_performance_report",
        create_performance_log_with_program)
    
# intent 4 ito
def handle_local_practice_log(chat_id, user_id, prompt):
    return handle_log(
        chat_id, 
        user_id, 
        prompt, 
        "prompts/ask_farmer_diy_log", 
        "",
        "log_diy_practice",
        create_health_incident_with_program)
    

    
def get_intent(prompt, prompt_file, function_name):
    return handle_intent(prompt, prompt_file, function_name)