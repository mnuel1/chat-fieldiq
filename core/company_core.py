

from typing import List
from config.config import get_supabase_client
from exceptions.global_exception import GlobalException


class Company:
    def __init__(self):
        self.client = get_supabase_client()

    # THIS IS FOR FARMERS ONLY
    def get_farmer_associated_company_id(self, farmer_user_profile_id: int) -> List[dict]:
        response = self.client.table("company_farmers") \
            .select("id") \
            .eq("farmer_user_profile_id", farmer_user_profile_id) \
            .execute()

        if response.data is None:
            raise GlobalException("No farmer found in the company.", 404)

        company_id = response.data[0].id

        return company_id
    
    # Function for fetching the ID of the user using user_profile_id
    # THIS IS FOR ADMIN/SALES REP
    @staticmethod
    def get_user_company(self, user_profile_id: int):
        response = self.client.table("user_profiles") \
            .select("company_id") \
            .eq("id", user_profile_id) \
            .execute()
        
        if response.data is None:
            raise GlobalException("The user is not associated to a company.", 404)
        
        company_id = response.data[0].id
        
        return company_id
