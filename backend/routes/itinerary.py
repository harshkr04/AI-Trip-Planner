# backend/routes/itinerary.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.planner_service import generate_full_plan

router = APIRouter()

class PlanRequest(BaseModel):
    prompt: str
    start_date: str
    end_date: str

@router.post("/generate")
def generate_itinerary(request: PlanRequest):
    try:
        trip = {
            "prompt": request.prompt,
            "start_date": request.start_date,
            "end_date": request.end_date
        }
        plan_result = generate_full_plan(trip)
        return plan_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate itinerary: {str(e)}")
