import os
import requests
import streamlit as st
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()
OPENTRIP_API_KEY = os.getenv("OPENTRIP_API_KEY")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")  # Add your Pexels API key to .env
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

PLACEHOLDER_IMAGE = "https://via.placeholder.com/300x200?text=No+Image"

def safe_rating(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0

def fetch_image(query):
    """Fetch image URL using Pexels -> Unsplash -> Wikimedia Commons -> Placeholder fallback."""

    # 1️⃣ Pexels
    try:
        pexels_url = f"https://api.pexels.com/v1/search?query={quote(query)}&per_page=1"
        headers = {"Authorization": PEXELS_API_KEY}
        res = requests.get(pexels_url, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data.get("photos"):
            return data["photos"][0]["src"]["medium"]
    except Exception as e:
        print(f"Pexels error: {e}")

    # 2️⃣ Unsplash
    try:
        unsplash_url = (
            f"https://api.unsplash.com/search/photos?"
            f"query={quote(query)}&client_id={UNSPLASH_ACCESS_KEY}&per_page=1"
        )
        res = requests.get(unsplash_url, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data.get("results"):
            return data["results"][0]["urls"]["regular"]
    except Exception as e:
        print(f"Unsplash error: {e}")

    # 3️⃣ Wikimedia Commons
    try:
        wiki_url = (
            f"https://commons.wikimedia.org/w/api.php"
            f"?action=query&format=json&prop=imageinfo&generator=search"
            f"&gsrsearch={quote(query)}&iiprop=url&gsrlimit=1"
        )
        res = requests.get(wiki_url, timeout=10)
        res.raise_for_status()
        data = res.json()
        pages = data.get("query", {}).get("pages", {})
        for _, page in pages.items():
            imageinfo = page.get("imageinfo", [])
            if imageinfo:
                return imageinfo[0]["url"]
    except Exception as e:
        print(f"Wikimedia error: {e}")

    # 4️⃣ Placeholder
    return PLACEHOLDER_IMAGE

def get_unsplash_image(query):
    # Kept only for backward compatibility, not used now
    return None

def get_place_details(place_id):
    try:
        url = f"https://api.opentripmap.com/0.1/en/places/xid/{place_id}"
        params = {"apikey": OPENTRIP_API_KEY}
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error getting place details: {e}")
    return {}

def get_places(city, kinds):
    try:
        url = f"https://api.opentripmap.com/0.1/en/places/geoname"
        params = {"name": city, "apikey": OPENTRIP_API_KEY}
        res = requests.get(url, params=params, timeout=10)
        if res.status_code != 200:
            return []
        city_data = res.json()
        if "lat" not in city_data or "lon" not in city_data:
            return []
        lat, lon = city_data["lat"], city_data["lon"]
        url = "https://api.opentripmap.com/0.1/en/places/radius"
        params = {
            "radius": 10000,
            "lon": lon,
            "lat": lat,
            "kinds": kinds,
            "format": "json",
            "limit": 8,
            "apikey": OPENTRIP_API_KEY
        }
        places_res = requests.get(url, params=params, timeout=10)
        if places_res.status_code != 200:
            return []
        places_data = places_res.json()
        return places_data if isinstance(places_data, list) else []
    except Exception as e:
        print(f"Error in get_places: {e}")
        return []

def get_hotels(city):
    kinds_list = ["accomodations", "hotels", "accommodation", "lodging"]
    for kinds in kinds_list:
        places = get_places(city, kinds)
        if places:
            return places[:8]
    return []

def get_cuisines(city):
    kinds_list = ["restaurants,foods", "restaurants", "foods", "food_and_drink", "cafes"]
    for kinds in kinds_list:
        places = get_places(city, kinds)
        if places:
            return places[:8]
    return []

def get_fake_offers(name):
    offers = [
        f"💰 10% off at {name}",
        f"🔥 Weekend Special Deal",
        f"📅 Book now & Save 15%",
        f"⭐ Free cancellation",
        f"🎁 Complimentary breakfast"
    ]
    return offers[hash(name) % len(offers)]

def get_fake_rating():
    ratings = [4.2, 4.5, 3.8, 4.7, 4.1, 3.9, 4.3, 4.6, 4.0]
    return ratings[hash("rating") % len(ratings)]

def render_place_card(place, place_type, img_size=(300, 200)):
    name = place.get("name", f"Unknown {place_type}")
    if not name or name.startswith("Unknown"):
        return False
    place_id = place.get("xid", "")
    details = get_place_details(place_id) if place_id else {}
    search_query = f"{name} {place_type}" if place_type else name
    
    # Use new fetch_image with fallback chain
    img_url = fetch_image(search_query)
    
    point = place.get("point", {})
    maps_link = (f"https://www.google.com/maps/search/?api=1&query={point['lat']},{point['lon']}"
                 if point and "lat" in point and "lon" in point
                 else f"https://www.google.com/maps/search/?api=1&query={quote(name)}")
    rating = get_fake_rating()
    offer = get_fake_offers(name)
    description = details.get("wikipedia_extracts", {}).get("text", "") or \
                  f"Experience the best {'accommodation' if place_type == 'hotel' else 'dining'} at {name}."
    if len(description) > 100:
        description = description[:97] + "..."

    card_html = f"""
    <div style="
        border: 1px solid #ddd; 
        border-radius: 10px; 
        overflow: hidden;
        margin: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        background: white;
        text-align: center;
        width: {img_size[0]}px;
    ">
        <img src="{img_url}" alt="{name}" style="width:{img_size[0]}px; height:{img_size[1]}px; object-fit: cover;">
        <div style="padding: 10px;">
            <h4 style="margin:5px 0;">{name}</h4>
            <p style="color: #ffa500;">⭐ {rating:.1f} / 5.0</p>
            <p style="font-size: 0.85em; color: #555;">{description}</p>
            <p style="color: green; font-weight: bold;">{offer}</p>
            <a href="{maps_link}" target="_blank" style="text-decoration:none; color:#007BFF;">📍 View on Maps</a>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    return True

def render_cards_in_grid(places, place_type, min_rating, show_offers):
    filtered_places = [p for p in places if get_fake_rating() >= min_rating]
    if show_offers:
        filtered_places = [p for p in filtered_places if get_fake_offers(p.get("name", ""))]

    if not filtered_places:
        st.warning(f"No {place_type}s match your filters.")
        return

    for i in range(0, len(filtered_places), 4):
        cols = st.columns(4)
        for col, place in zip(cols, filtered_places[i:i+4]):
            with col:
                render_place_card(place, place_type)

def render():
    st.title("🏨 Hotels & 🍽️ Cuisines Finder")

    st.sidebar.header("🔍 Filters")
    min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 4.0, 0.1)
    show_offers = st.sidebar.checkbox("Only Show Offers", value=False)

    city = st.text_input("🏙️ Enter City Name", "Paris")

    if st.button("🔍 Search Hotels & Restaurants"):
        with st.spinner(f"Searching in {city}..."):
            hotels = get_hotels(city)
            cuisines = get_cuisines(city)

        # Hotels Section
        st.subheader("🏨 Top Hotels")
        if hotels:
            render_cards_in_grid(hotels, "hotel", min_rating, show_offers)
        else:
            st.warning(f"No hotels found in {city}.")

        st.markdown("---")

        # Restaurants Section
        st.subheader("🍽️ Top Restaurants & Cuisines")
        if cuisines:
            render_cards_in_grid(cuisines, "restaurant", min_rating, show_offers)
        else:
            st.warning(f"No restaurants found in {city}.")

        st.markdown("---")
        st.markdown(
            "<div style='text-align:center;color:#666;padding:20px;'>🌟 Discover amazing places and create unforgettable memories! 🌟</div>",
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    render()
