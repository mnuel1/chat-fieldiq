from datetime import datetime
from typing import List, Optional, Dict
from config.config import get_supabase_client



class Farmer:
  def __init__(self):
    self.client = get_supabase_client()

  def get_feed_use(self, user_id: int) -> List[dict]:
    response = self.client.table("farmers") \
      .select("current_feed, days_on_feed") \
      .eq("id", user_id) \
      .execute()
    data = response.data[0] if response.data else {}
    return data.get("days_on_feed", 0), data.get("current_feed", "")
