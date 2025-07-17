from datetime import datetime, timezone
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

    def create_health_incident(self, farmer_user_profile_id: int, form_data: Dict):
        self.client.table("health_incidents").insert({
            "farmer_user_profile_id": farmer_user_profile_id,
            **form_data,
            "reported_by": farmer_user_profile_id,
            "updated_at": "now()", }).execute()
        return None

    def create_feed_calculation_log(self, user_profile_id: int, log_data: Dict) -> Dict:
        payload = {
            "user_profile_id": user_profile_id,
            **log_data
        }

        response = self.client.table(
            "feed_calculation_logs").insert(payload).execute()
        return response.data[0] if response.data else {}

    def update_feed_calculation_log(self, log_id: int, updated_data: Dict) -> Dict:
        payload = {
            **updated_data,
            "updated_at": datetime.now(timezone.utc)
        }

        response = self.client.table("feed_calculation_logs") \
            .update(payload) \
            .eq("id", log_id) \
            .execute()

        return response.data[0] if response.data else {}
