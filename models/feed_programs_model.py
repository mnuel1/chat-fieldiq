

from pydantic import BaseModel


class FeedProgramPayload(BaseModel):
  farmer_user_profile_id: int
  feed_product_id: int
  animal_quantity: int