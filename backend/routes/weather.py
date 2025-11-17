from fastapi import APIRouter, HTTPException
from ..services.weather_service import get_weather_for_trip

router = APIRouter()

@router.post("/")
async def weather_route(payload: dict):
    try:
        res = get_weather_for_trip(payload)
        return {"success": True, "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
