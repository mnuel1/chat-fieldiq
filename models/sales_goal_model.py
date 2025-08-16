from datetime import date
from pydantic import BaseModel
from typing import Optional

class SalesGoalBase(BaseModel):
    company_id: int
    target_amount: float
    period_start: date
    period_end: date
    created_by: int

class SalesGoalUpdate(BaseModel):
    target_amount: Optional[float] = None
