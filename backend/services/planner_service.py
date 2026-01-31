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
    
    # 1. Fetch Auxiliary Data
    weather = get_weather_for_trip(trip)
    flights = get_flight_options(trip)
    hotels = get_hotel_options(trip)
    
    context_data = {
        "weather": weather,
        "flights": flights,
        "hotels": hotels
    }
    
    # 2. Generate Itinerary via LLM
    # Note: llm_service.generate_itinerary now returns the full structured response
    response = llm_service.generate_itinerary(
        prompt=trip.get("prompt", ""),
        start_date=trip.get("start_date", ""),
        end_date=trip.get("end_date", ""),
        context_data=context_data
    )
    
    # 3. Add itinerary_text by rendering the structured itinerary
    if response.get("itinerary"):
        response["itinerary_text"] = render_itinerary_text(response["itinerary"])
    
    # 4. Return the response (it matches the required JSON structure)
    return response

def render_itinerary_text(itinerary_data: list) -> str:
    """
    Helper to convert the structured itinerary list to clean plain text
    for UI display and PDF generation. NO MARKDOWN.
    """
    lines = []
    
    # Add header if we have days
    if itinerary_data:
        first_day = itinerary_data[0] if isinstance(itinerary_data[0], dict) else itinerary_data[0].dict()
        last_day = itinerary_data[-1] if isinstance(itinerary_data[-1], dict) else itinerary_data[-1].dict()
        
        lines.append("TRIP ITINERARY")
        lines.append("")
        lines.append(f"Duration: {len(itinerary_data)} Days")
        lines.append("")
    
    for day in itinerary_data:
        # Handle both dict and Pydantic object
        d = day if isinstance(day, dict) else day.dict()
        
        # Day header (plain text, no markdown)
        lines.append(f"Day {d.get('day')} — {d.get('title')}")
        lines.append("")
        
        # Summary
        if d.get('summary'):
            lines.append(d.get('summary'))
            lines.append("")
        
        # Schedule
        for seg in d.get('schedule', []):
            s = seg if isinstance(seg, dict) else seg.dict()
            period = s.get('period', '')
            activity = s.get('activity', '')
            
            lines.append(f"{period}:")
            lines.append(f"  {activity}")
            
            if s.get('duration'):
                lines.append(f"  Duration: {s.get('duration')}")
            if s.get('travel_time'):
                lines.append(f"  Travel time: {s.get('travel_time')}")
            if s.get('booking_link'):
                lines.append(f"  Booking: {s.get('booking_link')}")
            if s.get('cost_estimate'):
                lines.append(f"  Cost: {s.get('cost_estimate')}")
            
            lines.append("")
        
        # Cost estimate
        if d.get('cost_estimate'):
            lines.append(f"Estimated cost for Day {d.get('day')}: {d.get('cost_estimate')}")
            lines.append("")
        
        # Notes
        if d.get('notes'):
            lines.append("Important Notes:")
            for note in d['notes']:
                lines.append(f"  • {note}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)

def refine_plan(itinerary: dict, instruction: str):
    # This needs a real LLM implementation too for "refinement", 
    # but for now we'll keep the logic simple or just append the instruction 
    # since the user asked to focus on "Primary generation".
    # However, to avoid breaking it, we'll adapt the existing logic to the new structure.
    
    # The 'itinerary' passed here is now the list of day objects (from the new structure)
    # or the full response dict? 
    # The route passes `record["itinerary"]`. In the new `generate_full_plan`, 
    # we return `response` which has `itinerary` as a list of days.
    # So `record["itinerary"]` will be that list.
    
    if not itinerary:
        raise ValueError("Itinerary is missing structured data to refine.")
        
    refined = deepcopy(itinerary) # This is a list of days now
    
    # Simple keyword-based refinement (legacy logic adapted)
    instruction_lower = instruction.lower()
    
    # Apply to all days for now as a simple heuristic
    for day in refined:
        if "adventure" in instruction_lower:
            day["title"] += " (Adventure Mode)"
            day["notes"].append("Added adventure focus based on request.")
        elif "budget" in instruction_lower:
            day["notes"].append("Budget tip: Use public transport and eat at local delis.")
        elif "relax" in instruction_lower:
             day["notes"].append("Relaxation focus: Take it slow today.")
        else:
             day["notes"].append(f"Note: {instruction}")

    new_text = render_itinerary_text(refined)
    
    return {
        "itinerary": refined,
        "itinerary_text": new_text,
        "explanation": "Updated itinerary based on your instructions.",
        "changed_days": [] # simplified
    }
