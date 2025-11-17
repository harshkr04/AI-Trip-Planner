import random

def get_flight_options(trip: dict):
    destination = trip.get("destination", "Unknown")
    start_date = trip.get("start_date", "2025-11-01")
    base_prices = {
        "Goa": 4500, "Mumbai": 3500, "Bangalore": 4000, "Chennai": 4500,
        "Jaipur": 3000, "Udaipur": 3500, "Manali": 5000, "Kerala": 5500,
        "Kolkata": 4000, "Hyderabad": 3500, "default": 4000
    }
    base_price = base_prices.get(destination, base_prices["default"])
    airlines = [("IndiGo", 0.9), ("Air India", 1.1), ("SpiceJet", 0.85), ("Vistara", 1.2)]
    flights = []
    times = ["06:00 AM", "09:30 AM", "02:15 PM", "06:45 PM"]
    for i, (airline, multiplier) in enumerate(airlines):
        price_variation = random.uniform(0.8, 1.2)
        final_price = int(base_price * multiplier * price_variation)
        flights.append({
            "airline": airline,
            "from": "Delhi",
            "to": destination,
            "depart": f"{start_date} {times[i]}",
            "price": final_price
        })
    flights.sort(key=lambda x: x["price"])
    return flights
