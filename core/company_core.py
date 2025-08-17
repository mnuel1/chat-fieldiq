

from typing import List
from config.config import get_supabase_client
from exceptions.global_exception import GlobalException


class Company:
    def __init__(self):
        self.client = get_supabase_client()

    # THIS IS FOR FARMERS ONLY
    def get_farmer_associated_company_id(self, farmer_user_profile_id: int) -> List[dict]:
        response = self.client.table("company_farmers") \
            .select("company_id") \
            .eq("farmer_user_profile_id", farmer_user_profile_id) \
            .execute()

        if response.data is None:
            raise GlobalException("No farmer found in the company.", 404)
        
        company_id = response.data[0]["company_id"]

        return company_id
    
    # Function for fetching the ID of the user using user_profile_id
    # THIS IS FOR ADMIN/SALES REP
    def get_user_company(self, user_profile_id: int):
        print(user_profile_id)
        # Get user role
        role_response = self.client.table("user_roles") \
            .select("role_id") \
            .eq("user_profile_id", user_profile_id) \
            .execute()

        if not role_response.data or len(role_response.data) == 0:
            raise GlobalException("User role not found.", 404)

        role_id = role_response.data[0]["role_id"]
        company_id = None
        # Check role and query company id accordingly
        if role_id in [1, 2]:
            response = self.client.table("user_profiles") \
                .select("company_id") \
                .eq("id", user_profile_id) \
                .execute()
            company_id = response.data[0]['company_id']
        elif role_id == 3:
            response = self.client.table("company_farmers") \
                .select("company_id") \
                .eq("farmer_user_profile_id", user_profile_id) \
                .execute()

            company_id = response.data[0]["company_id"]
        else:
            raise GlobalException("Unknown user role.", 400)

        if not response.data or len(response.data) == 0 or company_id == None:
            raise GlobalException("The user is not associated to a company.", 404)

        return company_id