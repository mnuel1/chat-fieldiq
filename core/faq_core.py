from datetime import datetime
from typing import List, Optional, Dict
from config.config import get_supabase_client



class Faq:
  def __init__(self):
    self.client = get_supabase_client()

  def insert_faq(self, question: str, answer: str, category: str):
    response = self.client.table("faq").insert({
      "category": category,
      "question": question,
      "answer": answer
    }).execute()

    return response.data[0]["id"] if response.data[0] else None
  
  def get_faq(self, limit: int = 10, offset: int = 0):
        
    category_counts = self.client.rpc("faq_category_counts").execute()

    if not category_counts.data:
        return []
    
    top_categories = sorted(
        category_counts.data, key=lambda x: x["count"], reverse=True
    )[:3]
    top_category_names = [cat["category"] for cat in top_categories]
    
    response = self.client.table("faq") \
        .select("*") \
        .in_("category", top_category_names) \
        .range(offset, offset + limit - 1) \
        .execute()

    return response.data if response.data else []
    