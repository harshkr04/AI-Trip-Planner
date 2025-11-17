import random

def get_hotel_options(trip: dict):
    destination = trip.get("destination", "Unknown")
    base_prices = {
        "Goa": 3000, "Mumbai": 4000, "Jaipur": 2500, "Kerala": 3500,
        "Bangalore": 3500, "Udaipur": 3000, "Manali": 2800, "default": 3000
    }
    base_price = base_prices.get(destination, base_prices["default"])
    hotel_types = [
        ("The Grand", "City Center", 4.5, 1.2),
        ("Budget Inn", "Tourist District", 3.8, 0.6),
        ("Luxury Palace", "Premium Zone", 4.8, 2.5),
        ("Comfort Stay", "Downtown", 4.2, 0.9),
        ("Backpacker Hostel", "Near Station", 4.0, 0.25)
    ]
    hotels = []
    for name_prefix, area, rating, multiplier in hotel_types:
        price_variation = random.uniform(0.75, 1.25)
        final_price = int(base_price * multiplier * price_variation)
        final_rating = round(rating + random.uniform(-0.2, 0.2), 1)
        hotels.append({
            "name": f"{name_prefix} {destination}",
            "area": area,
            "rating": max(3.0, min(5.0, final_rating)),
            "price_per_night": final_price
        })
    hotels.sort(key=lambda x: x["rating"], reverse=True)
    return hotels
