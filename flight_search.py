import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date
from agents.flight_price_finder import search_flights_with_fallback

# Page config
st.set_page_config(page_title="Flight Search", page_icon="✈️", layout="wide")

# Custom CSS for better UI
st.markdown("""
<style>
    .flight-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .price-highlight {
        color: #28a745;
        font-weight: bold;
        font-size: 18px;
    }
    .airline-name {
        color: #007bff;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Page Header
st.markdown("# ✈️ Flight Price Search")
st.markdown("### Find the best flight deals with real-time prices")

# Initialize session state
if "flight_results" not in st.session_state:
    st.session_state.flight_results = []
if "search_performed" not in st.session_state:
    st.session_state.search_performed = False

# Main search form
with st.container():
    st.markdown("## 🔍 Search Flights")
    
    # Create columns for better layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🛫 Departure Details**")
        from_city = st.selectbox(
            "From City",
            options=["Delhi (DEL)", "Mumbai (BOM)", "Bangalore (BLR)", "Chennai (MAA)", 
                    "Kolkata (CCU)", "Hyderabad (HYD)", "Pune (PNQ)", "Ahmedabad (AMD)",
                    "Goa (GOI)", "Jaipur (JAI)", "Kochi (COK)", "Lucknow (LKO)"],
            help="Select departure city"
        )
        
        # Extract airport code
        from_code = from_city.split("(")[1].replace(")", "") if "(" in from_city else from_city
        
    with col2:
        st.markdown("**🛬 Arrival Details**")
        to_city = st.selectbox(
            "To City",
            options=["Mumbai (BOM)", "Delhi (DEL)", "Bangalore (BLR)", "Chennai (MAA)", 
                    "Kolkata (CCU)", "Hyderabad (HYD)", "Pune (PNQ)", "Ahmedabad (AMD)",
                    "Goa (GOI)", "Jaipur (JAI)", "Kochi (COK)", "Lucknow (LKO)"],
            help="Select destination city"
        )
        
        # Extract airport code
        to_code = to_city.split("(")[1].replace(")", "") if "(" in to_city else to_city
        
    with col3:
        st.markdown("**📅 Travel Details**")
        travel_date = st.date_input(
            "Departure Date",
            min_value=date.today(),
            value=date.today(),
            help="Select your travel date"
        )
        
        passengers = st.selectbox(
            "Passengers",
            options=[1, 2, 3, 4, 5, 6],
            help="Number of passengers"
        )

# Additional options in expander
with st.expander("⚙️ Advanced Options"):
    col_adv1, col_adv2 = st.columns(2)
    
    with col_adv1:
        cabin_class = st.selectbox(
            "Cabin Class",
            options=["Economy", "Premium Economy", "Business", "First"],
            index=0
        )
        
    with col_adv2:
        currency = st.selectbox(
            "Currency",
            options=["INR", "USD", "EUR"],
            index=0
        )

# Search button
search_col1, search_col2, search_col3 = st.columns([1, 2, 1])
with search_col2:
    search_button = st.button(
        "🔍 Search Flights",
        type="primary",
        use_container_width=True,
        help="Click to search for available flights"
    )

# Handle search
if search_button:
    if from_code == to_code:
        st.error("❌ Departure and arrival cities cannot be the same!")
    else:
        with st.spinner(f"🔍 Searching flights from {from_city} to {to_city}..."):
            try:
                # Call updated flight search function with fallback
                flight_results = search_flights_with_fallback(
                    departure=from_code,
                    arrival=to_code,
                    depart_date=travel_date.strftime("%Y-%m-%d"),
                    adults=passengers,
                    currency=currency
                )
                
                st.session_state.flight_results = flight_results
                st.session_state.search_performed = True
                
                if flight_results:
                    st.success(f"✅ Found {len(flight_results)} flights!")
                else:
                    st.warning("⚠️ No flights found. Showing booking platforms below.")
                    
            except Exception as e:
                st.error(f"❌ Search failed: {str(e)}")
                st.info("💡 Make sure your SERPAPI_KEY is correctly set in .env file")
                st.session_state.flight_results = []
                st.session_state.search_performed = True

# Display Results
if st.session_state.search_performed:
    st.markdown("---")
    
    if st.session_state.flight_results:
        # Results found
        st.markdown(f"## ✈️ Flight Results: {from_city} → {to_city}")
        st.markdown(f"**📅 Date:** {travel_date.strftime('%B %d, %Y')} | **👥 Passengers:** {passengers}")
        
        # Display flights in cards
        for i, flight in enumerate(st.session_state.flight_results):
            with st.container():
                st.markdown(f"""
                <div class="flight-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span class="airline-name">{flight['airline']}</span> 
                            <span style="color: #666;">({flight['flight_number']})</span>
                        </div>
                        <div class="price-highlight">{flight['price']}</div>
                    </div>
                    <div style="margin-top: 10px;">
                        <strong>🛫 Departure:</strong> {flight['departure_time']} | 
                        <strong>🛬 Arrival:</strong> {flight['arrival_time']} | 
                        <strong>⏱️ Duration:</strong> {flight['duration_mins']}
                    </div>
                    <div style="margin-top: 5px; color: #666;">
                        <strong>Agent:</strong> {flight['agent']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Data table view
        with st.expander("📊 View as Table"):
            df = pd.DataFrame(st.session_state.flight_results)
            st.dataframe(df, use_container_width=True)
        
        # Price comparison chart
        try:
            prices = []
            airlines = []
            
            for flight in st.session_state.flight_results:
                price_str = str(flight.get('price', '0'))
                import re
                price_match = re.search(r'[\d,]+', price_str.replace('₹', ''))
                if price_match:
                    price_num = int(price_match.group().replace(',', ''))
                    prices.append(price_num)
                    airlines.append(flight.get('airline', 'Unknown'))
            
            if prices and len(prices) > 1:
                with st.expander("📈 Price Comparison Chart"):
                    fig, ax = plt.subplots(figsize=(12, 6))
                    bars = ax.bar(airlines, prices, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
                    
                    ax.set_ylabel("Price (₹)")
                    ax.set_title(f"Flight Prices: {from_city} → {to_city}")
                    ax.tick_params(axis='x', rotation=45)
                    
                    # Add price labels on bars
                    for bar, price in zip(bars, prices):
                        height = bar.get_height()
                        ax.text(bar.get_x() + bar.get_width()/2., height + max(prices)*0.01,
                               f'₹{price:,}', ha='center', va='bottom', fontweight='bold')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()
        except Exception as e:
            pass  # Skip chart if error
    
    else:
        # No results - show booking platforms
        st.markdown(f"## 🔗 Book on Popular Platforms")
        st.markdown(f"**Route:** {from_city} → {to_city} | **Date:** {travel_date.strftime('%B %d, %Y')}")
        
        # Create booking links
        date_str = travel_date.strftime("%Y-%m-%d")
        date_compact = travel_date.strftime("%Y%m%d")
        
        # Display booking platforms in grid
        col1, col2, col3 = st.columns(3)
        
        platforms = [
            ("Google Flights", f"https://www.google.com/flights?hl=en#flt={from_code}.{to_code}.{date_str}", "🔵"),
            ("Skyscanner", f"https://www.skyscanner.co.in/transport/flights/{from_code.lower()}/{to_code.lower()}/{date_compact}/", "🟢"),
            ("MakeMyTrip", f"https://www.makemytrip.com/flight/search?itinerary={from_code}-{to_code}-{date_str}", "🔴"),
            ("Cleartrip", f"https://www.cleartrip.com/flights/results?from={from_code}&to={to_code}&depart={date_str}&adults={passengers}", "🟠"),
            ("Goibibo", f"https://www.goibibo.com/flights/?from={from_code}&to={to_code}&depdate={date_str}&seatingclass=E&adults={passengers}", "🟡"),
            ("EaseMyTrip", f"https://www.easemytrip.com/flights/booking/{from_code}-{to_code}/D/{date_str}", "🟣")
        ]
        
        for i, (name, url, icon) in enumerate(platforms):
            col = [col1, col2, col3][i % 3]
            with col:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    margin: 10px 0;
                ">
                    <div style="font-size: 24px;">{icon}</div>
                    <div style="color: white; font-weight: bold; margin: 5px 0;">{name}</div>
                    <a href="{url}" target="_blank" style="
                        background: white;
                        color: #333;
                        padding: 5px 15px;
                        text-decoration: none;
                        border-radius: 5px;
                        font-weight: bold;
                    ">Search Flights</a>
                </div>
                """, unsafe_allow_html=True)

# Footer info
st.markdown("---")
st.markdown("""
### 💡 Tips for Better Results:
- **Book in advance** for better prices
- **Compare prices** across multiple platforms  
- **Check flexible dates** for cheaper options
- **Clear browser cookies** before booking
- **Use incognito mode** to avoid price tracking

### 🔑 API Information:
- Powered by **SerpAPI** (Google Flights data)
- Free tier: **100 searches/month**
- Get your API key: **https://serpapi.com/**
""")

# Add search again button
if st.session_state.search_performed:
    if st.button("🔄 Search Again", type="secondary"):
        st.session_state.flight_results = []
        st.session_state.search_performed = False
        st.rerun()