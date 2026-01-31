import json
import os
import uuid
from copy import deepcopy
from typing import Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STORE_FILE = os.path.join(BASE_DIR, "itinerary_store.json")

if not os.path.exists(STORE_FILE):
    with open(STORE_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)


def _load() -> Dict[str, Any]:
    try:
        with open(STORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: Dict[str, Any]) -> None:
    with open(STORE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _ensure_day_fields(itinerary_days: list) -> list:
    """
    Ensure each day in the itinerary list has the required fields.
    itinerary_days is now a list of day objects, not a dict with a 'days' key.
    """
    for day in itinerary_days:
        day.setdefault("personal_note", "")
        day.setdefault("notes", [])
    return itinerary_days


def create_record(plan_result: Dict[str, Any], metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
    store = _load()
    itinerary_id = str(uuid.uuid4())
    
    # plan_result["itinerary"] is now a list of days, not a dict with a "days" key
    itinerary_data = _ensure_day_fields(deepcopy(plan_result.get("itinerary", [])))
    
    record = {
        "id": itinerary_id,
        "itinerary": itinerary_data,
        "itinerary_text": plan_result.get("itinerary_text", ""),
        "prompt": metadata.get("prompt") if metadata else "",
        "conversation": metadata.get("conversation") if metadata and metadata.get("conversation") else [],
    }
    store[itinerary_id] = record
    _save(store)
    return record


def get_record(itinerary_id: str) -> Dict[str, Any] | None:
    store = _load()
    record = store.get(str(itinerary_id))
    if record:
        record["itinerary"] = _ensure_day_fields(record["itinerary"])
    return record


def update_record(itinerary_id: str, **fields: Any) -> Dict[str, Any]:
    store = _load()
    if itinerary_id not in store:
        raise KeyError("Itinerary not found")
    record = store[itinerary_id]
    if "itinerary" in fields and fields["itinerary"]:
        record["itinerary"] = _ensure_day_fields(deepcopy(fields["itinerary"]))
    if "itinerary_text" in fields and fields["itinerary_text"] is not None:
        record["itinerary_text"] = fields["itinerary_text"]
    if "conversation" in fields and fields["conversation"] is not None:
        record["conversation"] = fields["conversation"]
    store[itinerary_id] = record
    _save(store)
    return record


def save_day_note(itinerary_id: str, day_number: int, note: str) -> Dict[str, Any]:
    record = get_record(itinerary_id)
    if not record:
        raise KeyError("Itinerary not found")
    updated = False
    for day in record["itinerary"].get("days", []):
        if int(day.get("day", 0)) == int(day_number):
            day["personal_note"] = note
            updated = True
            break
    if not updated:
        raise KeyError("Day not found")
    update_record(itinerary_id, itinerary=record["itinerary"])
    return {"day": day_number, "personal_note": note}

