# backend/services/planner_service.py
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
    itinerary_text = llm_service.generate_itinerary(
        prompt=trip.get("prompt", ""),
        start_date=trip.get("start_date", ""),
        end_date=trip.get("end_date", ""),
        context=context
    )
    return {
        "itinerary_text": itinerary_text,
        "weather": weather,
        "flights": flights,
        "hotels": hotels
    }
