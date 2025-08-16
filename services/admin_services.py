from fastapi import APIRouter, Query

from models.faq_model import FAQBase, FAQUpdate
from core.chat_core import Chat
from core.admin_core import Admin

import random

from models.sales_goal_model import SalesGoalBase, SalesGoalUpdate

router = APIRouter()


# SALES DATA ROUTEs ------------------------------------------
@router.get("/sales")
def sales(company_id: int = Query(...)):
  try:
    admin = Admin()
    sales = admin.get_sales_data(company_id)
    return {"message": "Success", "data": sales}
  except Exception as e:
    print(f"An error occurred: {e}")
    return {"message": "Something went wrong", "data": None}

# SALES GOALS ROUTEs ------------------------------------------
@router.get("/sales-goals/current")
def get_current_sales_goal(company_id: int = Query(...)):
    """
    Get the currently active sales goal for a company.
    """
    try:
        admin = Admin()
        current_goal = admin.get_current_sales_goal(company_id)

        if not current_goal:
            return {"message": "No active sales goal found", "data": None}

        return {"message": "Success", "data": current_goal}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"message": "Something went wrong", "data": None}

@router.get("/sales-goals")
def get_sales_goals(company_id: int = Query(...)):
    """
    Fetch all sales goals for a company.
    Status (locked/active/future) is determined dynamically.
    """
    try:
        admin = Admin()
        goals = admin.get_sales_goals(company_id)
        return {"message": "Success", "data": goals}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"message": "Something went wrong", "data": None}

@router.post("/sales-goals")
def create_sales_goal(goal: SalesGoalBase):
    try:
        admin = Admin()
        new_goal = admin.create_sales_goal(
            goal.company_id,
            goal.target_amount,
            goal.period_start,
            goal.period_end,
            goal.created_by,
        )
        return {"message": "Success", "data": new_goal}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"message": "Something went wrong", "data": None}

@router.put("/sales-goals/{goal_id}")
def update_sales_goal(goal_id: int, updates: SalesGoalUpdate):
    try:
        admin = Admin()
        updated_goal = admin.update_sales_goal(
            goal_id,
            updates.model_dump(exclude_unset=True)
        )
        return {"message": "Success", "data": updated_goal}
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"message": "Something went wrong", "data": None}

# FARM ROUTEs ------------------------------------------
@router.get("/farms")
def farms(company_id: int = Query(...)):
  try:
    admin = Admin()
    farms = admin.get_farms(company_id)
    return {"message": "Success", "data": farms}
  except Exception as e:
    print(f"An error occurred: {e}")
    return {"message": "Something went wrong", "data": None}

@router.get("/dealers/issue")
def dealers_issue(company_id: int = Query(...)):
  try:
    admin = Admin()
    dealers = admin.get_dealers_issue(company_id)
    return {"message": "Success", "data": dealers}
  except Exception as e:
    print(f"An error occurred: {e}")
    return {"message": "Something went wrong", "data": None}

@router.get("/farm/performance")
def farm_performance(company_id: int = Query(...)):
  try:
    admin = Admin()
    performance = admin.get_farm_performance(company_id)
    return {"message": "Success", "data": performance}
  except Exception as e:
    print(f"An error occurred: {e}")
    return {"message": "Something went wrong", "data": None}

# FAQS ROUTEs ------------------------------------------
@router.get("/faqs")
def faqs(company_id: int):
  try:
    admin = Admin()
    faqs = admin.get_faqs(company_id)
    return {"message": "Success", "data": faqs}
  except Exception as e:
    print(f"An error occurred: {e}")
    return {"message": "Something went wrong", "data": None}

@router.post("/faqs")
def faqs(faq: FAQBase):
  try:
    admin = Admin()
    result = admin.create_faq(
      question=faq.question,
      answer=faq.answer,
      category=faq.category,
      is_featured=faq.is_featured
    )

    if not result:
      raise ValueError("Failed to create FAQ entry.")
    
    result.update({
      "status": "active",
      "priority": random.randint(1, 4),
      "views": random.randint(100, 5000),
      "lastUpdated": result.get("updated_at"),
      "createdBy": "Chat AI Assistant",
      "tags": [result["category"]],
    })
    
    return {"message": "Success", "data": result}
  except Exception as e:
    print(f"An error occurred: {e}")
    return {"message": "Something went wrong", "data": None}

@router.put("/faqs/{faq_id}")
def faqs(faq_id: int, updates: FAQUpdate):
  try:
    admin = Admin()
    result = admin.update_faq(faq_id, updates.dict(exclude_unset=True))
    if not result:
      raise ValueError("Failed to update FAQ entry.")
    
    return {"message": "Success", "data": result}
  except Exception as e:
    print(f"An error occurred: {e}")
    return {"message": "Something went wrong", "data": None}

@router.delete("/faqs/{faq_id}")
def faqs(faq_id: int):
  try:
    admin = Admin()
    success = admin.delete_faq(faq_id)
    if not success:
        raise ValueError("Failed to delete FAQ")    
    return {"message": "Success", "data": []}
  except Exception as e:
    print(f"An error occurred: {e}")
    return {"message": "Something went wrong", "data": None}


#@router.post("/request/collateral")
def request_collateral():
  return 1
