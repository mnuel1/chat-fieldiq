from datetime import datetime
from typing import List, Optional, Dict
from config.config import get_supabase_client


class SalesRep:
    def __init__(self):
        self.client = get_supabase_client()
   
    def create_field_product_incident(self, reported_by: int, form_data: Dict, tag: str):
        self.client.table("field_product_incidents").insert({            
            **form_data,
            "tag": tag,
            "reported_by": reported_by,
            "updated_at": "now()", }).execute()
        return None
    
    def create_dealer_incident(self, reported_by: int, form_data: Dict, tag: str):
        self.client.table("dealer_incidents").insert({            
            **form_data,
            "tag": tag, 
            "reported_by": reported_by,
            "updated_at": "now()", }).execute()
        return None
    
    def get_alert_incidents(self, user_id: int) -> Dict[str, List[Dict]]:        
        field_incidents_resp = self.client.table("field_product_incidents").select("*").eq("reported_by", user_id).execute()
        dealer_incidents_resp = self.client.table("dealer_incidents").select("*").eq("reported_by", user_id).execute()

        field_incidents = field_incidents_resp.data if hasattr(field_incidents_resp, "data") else []
        dealer_incidents = dealer_incidents_resp.data if hasattr(dealer_incidents_resp, "data") else []

        return {
            "field_product_incidents": field_incidents,
            "dealer_incidents": dealer_incidents
        }