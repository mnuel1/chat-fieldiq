from pydantic import BaseModel
from typing import Optional

class FAQBase(BaseModel):
  question: str
  answer: str
  category: str
  is_featured: Optional[bool] = False

class FAQUpdate(BaseModel):
  question: Optional[str]
  answer: Optional[str]
  category: Optional[str]
  is_featured: Optional[bool]