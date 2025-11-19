# backend/routes/itinerary.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.planner_service import generate_full_plan, refine_plan
from ..services import itinerary_store
from typing import Optional

router = APIRouter()

class PlanRequest(BaseModel):
    prompt: str
    start_date: str
    end_date: str

class RefineRequest(BaseModel):
    itinerary_id: str
    instruction: str


class NoteRequest(BaseModel):
    note: str

@router.post("/generate")
def generate_itinerary(request: PlanRequest):
    try:
        trip = {
            "prompt": request.prompt,
            "start_date": request.start_date,
            "end_date": request.end_date
        }
        plan_result = generate_full_plan(trip)
        record = itinerary_store.create_record(
            plan_result,
            metadata={
                "prompt": request.prompt,
                "conversation": [
                    {"role": "assistant", "content": "Your itinerary is ready! Ask for tweaks below to refine specific days."}
                ],
            },
        )
        response = {
            **plan_result,
            "itinerary_id": record["id"],
            "conversation": record["conversation"],
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate itinerary: {str(e)}")

@router.post("/refine")
def refine_itinerary(request: RefineRequest):
    try:
        record = itinerary_store.get_record(request.itinerary_id)
        if not record:
            raise HTTPException(status_code=404, detail="Itinerary not found.")
        result = refine_plan(record["itinerary"], request.instruction)
        conversation = record.get("conversation", [])
        conversation.append({"role": "user", "content": request.instruction})
        assistant_msg = result.get("explanation") or "Plan updated with your instructions."
        conversation.append({"role": "assistant", "content": assistant_msg})
        itinerary_store.update_record(
            request.itinerary_id,
            itinerary=result["itinerary"],
            itinerary_text=result["itinerary_text"],
            conversation=conversation[-20:],
        )
        return {
            "itinerary_id": request.itinerary_id,
            "changed_days": result.get("changed_days", []),
            "itinerary_text": result["itinerary_text"],
            "message": assistant_msg,
            "conversation": conversation[-20:],
            "itinerary": result["itinerary"],
        }
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refine itinerary: {str(e)}")


@router.post("/{itinerary_id}/day/{day_number}/note")
def save_day_note(itinerary_id: str, day_number: int, payload: NoteRequest):
    try:
        result = itinerary_store.save_day_note(itinerary_id, day_number, payload.note)
        return {"status": "ok", **result}
    except KeyError as err:
        raise HTTPException(status_code=404, detail=str(err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unable to save note: {str(e)}")
