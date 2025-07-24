from datetime import datetime, timezone
from typing import List, Optional, Dict
from config.config import get_supabase_client


class Farmer:
    def __init__(self):
        self.client = get_supabase_client()

    def get_feed_use(self, user_id: int) -> List[dict]:
        # Get latest feed usage
        feed_usage_response = self.client.table("feed_usage_logs").select("*") \
            .eq("farmer_user_profile_id", user_id) \
            .order("created_at", desc=True).limit(1).execute()

        feed_usage = feed_usage_response.data[0] if feed_usage_response.data else None
        if not feed_usage:
            raise GlobalException(
                "No feed usage logs found.", status_code=404)

        start_date = feed_usage["start_date"]
        end_date = feed_usage.get("end_date")
        feed_product_id = feed_usage["feed_product_id"]

        date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")

        current_date = datetime.now()
        days_used = (current_date - date).days

        # Get feed product info
        feed_product_response = self.client.table("feed_products").select("*") \
            .eq("id", feed_product_id).single().execute()

        feed_product = feed_product_response.data or {}
        return days_used, feed_product.get("name", "")

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
