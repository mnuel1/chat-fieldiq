

from typing import List
from config.config import get_supabase_client
from exceptions.global_exception import GlobalException


class Company:
    def __init__(self):
        self.client = get_supabase_client()

    def get_farmer_associated_company_id(self, farmer_user_profile_id: int) -> List[dict]:
        respone = self.client.table("company_farmers") \
            .select("id") \
            .eq("farmer_user_profile_id", farmer_user_profile_id) \
            .execute()

        if respone.data is None:
            raise GlobalException("No farmer found in the company.", 404)

        company_id = respone.data[0].id

        return company_id
