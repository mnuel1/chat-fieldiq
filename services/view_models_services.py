from fastapi import APIRouter, HTTPException
from core.view_models_core import ViewModelsCore


router = APIRouter()


@router.get("/farmer-dashboard/{farmer_user_profile_id}")
def get_farmer_dashboard_view_model(farmer_user_profile_id: int):
    if farmer_user_profile_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user profile ID.")

    view_model_service = ViewModelsCore()

    return view_model_service.read_farmer_dashboard_view_model(farmer_user_profile_id)
