from datetime import datetime
from typing import Optional
from pydantic import BaseModel



class FeedCalculatorDto(BaseModel):
  id: int
  farmer_user_profile_id: int
  number_of_animals: int
  feed_frequency: int
  bag_size_kg: int
  current_stock_bags: int
  bag_cost_php: float
  animal_type: str
  feed_stage: str
  daily_consumption_kg: float
  bags_needed_per_week: float
  cost_per_week_php: float
  reorder_point_days: float
  alert_level: str
  weekly_consumption_kg: float
  created_at: datetime
  updated_at: Optional[datetime] = None
  
class FeedCalculationResponse(BaseModel):
    message: str
    data: FeedCalculatorDto
    
class CreateFeedCalculatorPayload(BaseModel):
  # farmer_user_profile_id: int
  user_profile_id: int
  number_of_animals: int
  feed_frequency: int
  bag_size_kg: int
  current_stock_bags: int
  bag_cost_php: float
  animal_type: str
  feed_stage: str
  daily_consumption_kg: float
  bags_needed_per_week: float
  cost_per_week_php: float
  reorder_point_days: float
  alert_level: str
  weekly_consumption_kg: float
  
class UpdateFeedCalculatorPayload(BaseModel):
  id: int
  # farmer_user_profile_id: int
  user_profile_id: int
  number_of_animals: int
  feed_frequency: int
  bag_size_kg: int
  current_stock_bags: int
  bag_cost_php: float
  animal_type: str
  feed_stage: str
  daily_consumption_kg: float
  bags_needed_per_week: float
  cost_per_week_php: float
  reorder_point_days: float
  alert_level: str
  weekly_consumption_kg: float
  created_at: str
  updated_at: str
  
  