# backend/services/planner_service.py
from copy import deepcopy
from datetime import datetime

from .weather_service import get_weather_for_trip
from .flight_service import get_flight_options
from .hotel_service import get_hotel_options
from ..llm_service import llm_service

def _extract_destination_from_prompt(prompt: str):
    if not prompt:
        return "Mumbai"
    cities = [
        "Goa", "Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad",
        "Jaipur", "Udaipur", "Manali", "Shimla", "Kerala", "Kochi", "Mysore",
        "Pune", "Agra", "Varanasi", "Rishikesh", "Darjeeling", "Ooty", "Guwahati",
        "Rajasthan", "Kashmir", "Ladakh", "Andaman", "Hampi", "Pondicherry"
    ]
    prompt_lower = prompt.lower()
    found_cities = [city for city in cities if city.lower() in prompt_lower]
    if found_cities:
        return found_cities[0]
    words = prompt.split()
    for word in words:
        clean = word.strip(",.!?")
        if clean and clean[0].isupper() and len(clean) > 3:
            skip = {"Plan", "Create", "Trip", "Travel", "Holiday", "Vacation", "Tour", "Visit"}
            if clean not in skip:
                return clean
    return "Mumbai"

def _apply_keyword_overrides(day, keyword):
    keyword = keyword.lower()
    if keyword == "adventure":
        day["highlights"] = "Dialled-up adventure day with guided thrills."
        for seg in day.get("segments", []):
            if seg["period"].lower() == "afternoon":
                seg["activity"] = "Guided canyon trek + cliff viewpoints with certified expert."
            if seg["period"].lower() == "evening":
                seg["activity"] = "Campfire storytelling with local guides."
        day["notes"].append("Adventure upgrade applied — carry sports shoes & hydration pack.")
    elif keyword == "budget":
        day["budget_tip"] = "Switch to boutique homestays (₹2-3k) and shared cabs to cut costs."
        day["notes"].append("Saved approx ₹1500 by using budget dining & metro cards.")
    elif keyword == "nightlife":
        for seg in day.get("segments", []):
            if seg["period"].lower() == "evening":
                seg["activity"] = "Nightlife crawl — craft cocktail bar + live indie gig."
        day["notes"].append("Added nightlife focus; arrange return cab in advance.")
    elif keyword == "relax":
        if day["segments"]:
            day["segments"][0]["activity"] = "Slow brunch + spa ritual / steam session."
        day["notes"].append("Reset the pace with restorative wellness slots.")

def generate_full_plan(trip: dict):
    destination = trip.get("destination")
    if not destination:
        destination = _extract_destination_from_prompt(trip.get("prompt", ""))
        trip["destination"] = destination
    weather = get_weather_for_trip(trip)
    flights = get_flight_options(trip)
    hotels = get_hotel_options(trip)
    ctx_lines = [
        f"Destination: {destination}",
        f"Travel Dates: {trip.get('start_date')} to {trip.get('end_date')}"
    ]
    if weather and weather.get("days"):
        ctx_lines.append(f"Weather: {weather.get('summary', '')}")
        for day in weather["days"][:5]:
            ctx_lines.append(f"  {day['date']}: {day['temp']}°C, {day['icon']}")
    if flights:
        ctx_lines.append("Available Flights:")
        for f in flights[:3]:
            ctx_lines.append(f"  {f['airline']}: {f['from']} → {f['to']} at {f.get('depart', '')} (₹{f['price']})")
    if hotels:
        ctx_lines.append("Recommended Hotels:")
        for h in hotels[:3]:
            ctx_lines.append(f"  {h['name']} - {h.get('area', '')}, ₹{h['price_per_night']}/night, {h['rating']}★")
    context = "\n".join(ctx_lines)
    itinerary_payload = llm_service.generate_itinerary(
        prompt=trip.get("prompt", ""),
        start_date=trip.get("start_date", ""),
        end_date=trip.get("end_date", ""),
        context=context,
        weather_days=weather.get("days") if weather else None,
    )
    itinerary_plan = itinerary_payload.get("plan")
    return {
        "itinerary_text": itinerary_payload.get("text"),
        "itinerary": itinerary_plan,
        "weather": weather,
        "flights": flights,
        "hotels": hotels
    }

def refine_plan(itinerary: dict, instruction: str):
    if not itinerary or not itinerary.get("days"):
        raise ValueError("Itinerary is missing structured data to refine.")
    refined = deepcopy(itinerary)
    instruction_lower = instruction.lower()
    day_targets = []
    for day in refined["days"]:
        token = f"day {day['day']}"
        if token in instruction_lower:
            day_targets.append(day)
    if not day_targets:
        day_targets = refined["days"]

    applied_tags = []
    if any(word in instruction_lower for word in ["adventure", "adventurous", "thrill"]):
        for day in day_targets:
            _apply_keyword_overrides(day, "adventure")
        applied_tags.append("adventure")
    if "budget" in instruction_lower or "cheap" in instruction_lower:
        for day in day_targets:
            _apply_keyword_overrides(day, "budget")
        applied_tags.append("budget")
    if "nightlife" in instruction_lower or "party" in instruction_lower:
        for day in day_targets:
            _apply_keyword_overrides(day, "nightlife")
        applied_tags.append("nightlife")
    if "relax" in instruction_lower or "slow" in instruction_lower or "spa" in instruction_lower:
        for day in day_targets:
            _apply_keyword_overrides(day, "relax")
        applied_tags.append("relax")
    if "hotel" in instruction_lower or "stay" in instruction_lower:
        for day in day_targets:
            day["notes"].append("Added boutique hotel suggestion: riverside stay with breakfast.")
        applied_tags.append("accommodation")
    if "travel time" in instruction_lower:
        for day in day_targets:
            day["travel_time"] = "Optimised route — under 20 mins between stops."
        applied_tags.append("logistics")

    if not applied_tags:
        for day in day_targets:
            day["notes"].append(instruction.strip())
        applied_tags.append("custom-note")

    refined.setdefault("refinements", []).append({
        "instruction": instruction,
        "applied_tags": applied_tags,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

    new_text = llm_service.render_plan_text(refined)
    summary = f"Applied refinement ({', '.join(applied_tags)})."
    changed_days = [
        {
            "day": day["day"],
            "data": day
        }
        for day in day_targets
    ]
    return {
        "itinerary": refined,
        "itinerary_text": new_text,
        "explanation": summary,
        "changed_days": changed_days
    }
