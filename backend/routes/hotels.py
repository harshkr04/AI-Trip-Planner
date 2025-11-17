# backend/routes/flights.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import random

router = APIRouter()

class FlightsReq(BaseModel):
    origin: str
    destination: str
    start_date: str

@router.post("/")
def flights_route(payload: FlightsReq):
    try:
        # simple mock flight generator (replace with real API calls)
        origin = payload.origin
        dest = payload.destination
        date = payload.start_date
        airlines = ["SpiceJet", "IndiGo", "Vistara", "Air India", "GoAir"]
        flights = []
        for i in range(4):
            depart_hour = random.choice([6, 9, 12, 15, 18, 21])
            depart = f"{date} {depart_hour:02d}:00"
            price = random.randint(2500, 8000)
            flights.append({
                "airline": airlines[i % len(airlines)],
                "from": origin,
                "to": dest,
                "depart": depart,
                "price": price
            })
        return {"success": True, "data": flights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
