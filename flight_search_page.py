# pages/flight_search_page.py - Improved Version with Better Error Handling

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import re

# Airport code mapping for common cities
AIRPORT_CODES = {
    'new delhi': 'DEL',
    'delhi': 'DEL',
    'mumbai': 'BOM',
    'bangalore': 'BLR',
    'bengaluru': 'BLR',
    'chennai': 'MAA',
    'kolkata': 'CCU',
    'hyderabad': 'HYD',
    'pune': 'PNQ',
    'ahmedabad': 'AMD',
    'goa': 'GOI',
    'jaipur': 'JAI',
    'kochi': 'COK',
    'lucknow': 'LKO',
    'chandigarh': 'IXC',
    'indore': 'IDR',
    'bhubaneswar': 'BBI',
    'coimbatore': 'CJB',
    'mangalore': 'IXE',
    'thiruvananthapuram': 'TRV',
    'trivandrum': 'TRV',
    'new york': 'JFK',
    'london': 'LHR',
    'dubai': 'DXB',
    'singapore': 'SIN',
    'bangkok': 'BKK',
    'kuala lumpur': 'KUL',
    'paris': 'CDG',
    'amsterdam': 'AMS',
    'frankfurt': 'FRA',
    'tokyo': 'NRT',
    'hong kong': 'HKG',
    'sydney': 'SYD',
    'melbourne': 'MEL',
    'toronto': 'YYZ',
    'vancouver': 'YVR',
    'los angeles': 'LAX',
    'san francisco': 'SFO',
    'chicago': 'ORD',
    'boston': 'BOS',
    'washington': 'DCA',
    'miami': 'MIA'
}

def render():
    """Render the flight search page"""

    # Try to import the flight search function with better error handling
    try:
        from agents.flight_price_finder import search_flights_with_fallback
    except ImportError as e:
        st.error(f"❌ Flight search module not found: {str(e)}")
        st.info("💡 Please check if the file 'agents/flight_price_finder.py' exists and contains 'search_flights_with_fallback' function")
        return
    except Exception as e:
        st.error(f"❌ Error importing flight search module: {str(e)}")
        return

    st.markdown("# ✈️ Flight Price Search")
    st.markdown("### 🔍 Find the best flight deals with real-time prices")

    # Back button
    col_back, col_empty = st.columns([1, 4])
    with col_back:
        if st.button("← Back to Itinerary", type="secondary"):
            st.session_state.current_page = "main"
            st.rerun()

    # Initialize session state
    if "flight_results" not in st.session_state:
        st.session_state.flight_results = []
    if "search_performed" not in st.session_state:
        st.session_state.search_performed = False

    # Get prefill data
    prefill_data = get_prefill_data()

    # Search form
    with st.container():
        st.markdown("## 🔍 Search Flights")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**🛫 Departure Details**")
            from_city_input = st.text_input(
                "From City / Airport",
                value=prefill_data.get("from_city", ""),
                help="Enter departure city (e.g., New Delhi, Mumbai, New York)"
            )
            # Show detected airport code
            from_code = get_airport_code(from_city_input)
            if from_code:
                st.caption(f"✅ Airport Code: {from_code}")
            elif from_city_input:
                st.caption("❌ Airport code not found")

        with col2:
            st.markdown("**🛬 Arrival Details**")
            to_city_input = st.text_input(
                "To City / Airport",
                value=prefill_data.get("to_city", ""),
                help="Enter destination city (e.g., London, Dubai, Singapore)"
            )
            # Show detected airport code
            to_code = get_airport_code(to_city_input)
            if to_code:
                st.caption(f"✅ Airport Code: {to_code}")
            elif to_city_input:
                st.caption("❌ Airport code not found")

        with col3:
            st.markdown("**📅 Travel Details**")
            travel_date = st.date_input(
                "Departure Date",
                min_value=date.today(),
                value=prefill_data.get("travel_date", date.today()),
                help="Select your travel date"
            )

            passengers = st.selectbox(
                "Passengers",
                options=[1, 2, 3, 4, 5, 6],
                index=prefill_data.get("passengers_index", 0),
                help="Number of passengers"
            )

    # Show popular airport codes for reference
    with st.expander("📋 Popular Airport Codes"):
        st.write("**Indian Cities:** DEL (Delhi), BOM (Mumbai), BLR (Bangalore), MAA (Chennai), CCU (Kolkata)")
        st.write("**International:** JFK/LGA (New York), LHR (London), DXB (Dubai), SIN (Singapore), BKK (Bangkok)")

    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        col_adv1, col_adv2, col_adv3 = st.columns(3)

        with col_adv1:
            cabin_class = st.selectbox("Cabin Class", ["Economy", "Premium Economy", "Business", "First"], index=0)
        with col_adv2:
            currency = st.selectbox("Currency", ["INR", "USD", "EUR"], index=0)
        with col_adv3:
            trip_type = st.selectbox("Trip Type", ["One Way", "Round Trip"], index=0)

    # Search button
    search_col1, search_col2, search_col3 = st.columns([1, 2, 1])
    with search_col2:
        search_button = st.button(
            "🔍 Search Flights",
            type="primary",
            use_container_width=True,
            help="Click to search for available flights"
        )

    # Handle search button click
    if search_button:
        if not from_city_input.strip() or not to_city_input.strip():
            st.error("❌ Please enter both departure and arrival cities!")
        elif from_code == to_code and from_code:
            st.error("❌ Departure and arrival cities cannot be the same!")
        elif not from_code or not to_code:
            st.error("❌ Please enter valid city names. Check the popular airport codes above for reference.")
        else:
            perform_flight_search(from_code, to_code, from_city_input, to_city_input, travel_date, passengers, currency, search_flights_with_fallback)

    # Display results if search was performed
    if st.session_state.search_performed:
        st.markdown("---")
        display_flight_results(from_city_input or "", to_city_input or "", travel_date, passengers)
        display_tips_and_info()

def get_airport_code(city_input):
    """Get airport code from city input using multiple methods"""
    if not city_input:
        return ""
    
    city_lower = city_input.lower().strip()
    
    # Method 1: Extract from brackets (e.g., "New Delhi (DEL)")
    if "(" in city_input and ")" in city_input:
        code = city_input.split("(")[1].replace(")", "").strip().upper()
        if len(code) == 3 and code.isalpha():
            return code
    
    # Method 2: Check if input is already a 3-letter code
    if len(city_lower) == 3 and city_lower.isalpha():
        return city_lower.upper()
    
    # Method 3: Look up in our mapping
    if city_lower in AIRPORT_CODES:
        return AIRPORT_CODES[city_lower]
    
    # Method 4: Try partial matches for common variations
    for city, code in AIRPORT_CODES.items():
        if city in city_lower or city_lower in city:
            return code
    
    return ""

def get_prefill_data():
    """Get prefill data from session state"""
    prefill = {}
    try:
        if "state" in st.session_state and st.session_state.state.get("preferences"):
            prefs = st.session_state.state["preferences"]
            from_loc = prefs.get("From", "")
            dest = prefs.get("destination", "")
            
            if from_loc:
                prefill["from_city"] = from_loc
            if dest:
                prefill["to_city"] = dest
                
            from_date = prefs.get("from_date")
            if from_date:
                try:
                    import datetime
                    prefill["travel_date"] = datetime.datetime.strptime(from_date, "%Y-%m-%d").date()
                except:
                    prefill["travel_date"] = date.today()
                    
            num_people = prefs.get("num_people", "1")
            if str(num_people).isdigit():
                idx = min(int(num_people) - 1, 5)
                prefill["passengers_index"] = max(0, idx)
    except Exception as e:
        st.warning(f"Could not load prefill data: {str(e)}")
    
    return prefill

def perform_flight_search(from_code, to_code, from_city, to_city, travel_date, passengers, currency, search_function):
    """Perform flight search with enhanced error handling"""
    with st.spinner(f"🔍 Searching flights from {from_city} to {to_city}..."):
        try:
            # Log the search parameters for debugging
            st.write(f"Debug: Searching {from_code} → {to_code} on {travel_date.strftime('%Y-%m-%d')}")
            
            flight_results = search_function(
                departure=from_code,
                arrival=to_code,
                depart_date=travel_date.strftime("%Y-%m-%d"),
                adults=passengers,
                currency=currency
            )
            
            st.session_state.flight_results = flight_results if flight_results else []
            st.session_state.search_performed = True
            
            if flight_results and len(flight_results) > 0:
                st.success(f"✅ Found {len(flight_results)} flights!")
            else:
                st.warning("⚠️ No flights found via API. This could be due to:")
                st.write("• Invalid airport codes")
                st.write("• No flights available for selected date")
                st.write("• API rate limits or connectivity issues")
                st.write("• Invalid API key configuration")
                st.info("💡 Showing booking platforms below where you can search manually.")
                
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ Search failed: {error_msg}")
            
            # Provide specific help based on error type
            if "400" in error_msg or "departure_id" in error_msg:
                st.info("💡 This error suggests the airport code format is incorrect. Try using 3-letter IATA codes.")
            elif "401" in error_msg or "API" in error_msg:
                st.info("💡 Make sure your SERPAPI_KEY is correctly set in .env file")
            elif "403" in error_msg:
                st.info("💡 API access forbidden. Check your API key permissions.")
            elif "429" in error_msg:
                st.info("💡 Rate limit exceeded. Please wait a moment before trying again.")
            else:
                st.info("💡 General error occurred. Check your internet connection and API configuration.")
            
            st.session_state.flight_results = []
            st.session_state.search_performed = True

def display_flight_results(from_city, to_city, travel_date, passengers):
    """Display flight search results using only native Streamlit components"""
    if st.session_state.flight_results and len(st.session_state.flight_results) > 0:
        st.markdown(f"## ✈️ Flight Results: {from_city} → {to_city}")
        st.markdown(f"**📅 Date:** {travel_date.strftime('%B %d, %Y')} | **👥 Passengers:** {passengers}")
        
        # Sort flights by price
        flights = sort_flights_by_price(st.session_state.flight_results)
        
        # Display flight cards using native components only
        for i, flight in enumerate(flights):
            display_flight_card_native(flight, i)
        
        # Data table view
        with st.expander("📊 View as Data Table"):
            try:
                df = pd.DataFrame(flights)
                st.dataframe(df, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not display data table: {str(e)}")
                st.json(flights)  # Fallback to JSON view
        
        # Price chart
        display_price_chart(flights, from_city, to_city)
    else:
        display_booking_platforms_native(from_city, to_city, travel_date, passengers)

def sort_flights_by_price(flights):
    """Sort flights by price with better error handling"""
    def extract_price(flight):
        try:
            price_str = str(flight.get('price', '0'))
            # Handle different price formats
            price_str = price_str.replace('₹', '').replace('$', '').replace('€', '').replace(',', '').replace(' ', '')
            
            # Extract numbers using regex
            price_match = re.search(r'\d+', price_str)
            return int(price_match.group()) if price_match else 999999
        except (ValueError, AttributeError):
            return 999999
    
    try:
        return sorted(flights, key=extract_price)
    except Exception as e:
        st.warning(f"Could not sort flights by price: {str(e)}")
        return flights

def display_flight_card_native(flight, index):
    """Display flight card using ONLY native Streamlit components"""
    # Price rank indicators
    price_indicators = ["🏆 BEST PRICE", "💎 VALUE DEAL", "✈️ AVAILABLE"]
    indicator = price_indicators[min(index, 2)]
    
    # Create a container with visual separation
    with st.container():
        st.markdown("---")
        
        # Header row with airline info and price
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Airline name and flight number
            airline = flight.get('airline', 'Unknown Airline')
            flight_num = flight.get('flight_number', 'N/A')
            st.subheader(f"✈️ {airline}")
            if flight_num != 'N/A':
                st.caption(f"Flight: {flight_num} | {indicator}")
            else:
                st.caption(indicator)
        
        with col2:
            # Price display
            price = flight.get('price', 'N/A')
            st.metric("Price", price)
        
        # Flight details row
        detail_col1, detail_col2, detail_col3 = st.columns(3)
        
        with detail_col1:
            st.write("**🛫 Departure**")
            departure = flight.get('departure_time', 'N/A')
            st.info(f"⏰ {departure}")
        
        with detail_col2:
            st.write("**🛬 Arrival**")
            arrival = flight.get('arrival_time', 'N/A')
            st.info(f"⏰ {arrival}")
        
        with detail_col3:
            st.write("**⏱️ Duration**")
            duration = flight.get('duration_mins', flight.get('duration', 'N/A'))
            st.success(f"🕐 {duration}")
        
        # Additional details
        details_col1, details_col2 = st.columns(2)
        with details_col1:
            stops = flight.get('stops', 'Direct')
            st.caption(f"🔄 **Stops:** {stops}")
        
        with details_col2:
            agent = flight.get('agent', flight.get('booking_agent', 'Multiple platforms'))
            st.caption(f"🏢 **Booking:** {agent}")
        
        # Booking button if available
        booking_url = flight.get('booking_url', flight.get('url'))
        if booking_url:
            st.link_button(
                f"Book with {agent}",
                booking_url,
                help=f"Book this flight via {agent}",
                use_container_width=True
            )

def display_booking_platforms_native(from_city, to_city, travel_date, passengers):
    """Display booking platforms using native Streamlit link buttons"""
    st.markdown("### 🌍 Search & Book Flights")
    st.write("No API results found. Search manually on these trusted platforms:")
    
    # Get airport codes for URL construction
    from_code = get_airport_code(from_city)
    to_code = get_airport_code(to_city)
    
    # Fallback to city names if no codes found
    from_param = from_code if from_code else from_city.replace(" ", "")
    to_param = to_code if to_code else to_city.replace(" ", "")
    
    # Create URLs with better formatting
    date_str = travel_date.strftime('%Y-%m-%d')
    date_short = travel_date.strftime('%y%m%d')
    
    google_url = f"https://www.google.com/flights?hl=en#flt={from_param}.{to_param}.{date_str};c:INR;e:1;sd:1;t:f;tt:o"
    skyscanner_url = f"https://www.skyscanner.net/transport/flights/{from_param}/{to_param}/{date_short}/?adults={passengers}"
    kayak_url = f"https://www.kayak.com/flights/{from_param}-{to_param}/{date_str}/{passengers}adults"
    expedia_url = f"https://www.expedia.com/Flights-Search?trip=oneway&leg1=from:{from_param},to:{to_param},departure:{date_str}TANYT&passengers=adults:{passengers}"
    
    # Display as columns with native buttons
    col1, col2 = st.columns(2)
    
    with col1:
        st.link_button(
            "🔍 Google Flights",
            google_url,
            help="Compare prices and airlines on Google Flights",
            use_container_width=True
        )
        
        st.link_button(
            "✈️ Skyscanner", 
            skyscanner_url,
            help="Find cheap flights on Skyscanner",
            use_container_width=True
        )
    
    with col2:
        st.link_button(
            "🌐 Kayak",
            kayak_url,
            help="Search and compare on Kayak",
            use_container_width=True
        )
        
        st.link_button(
            "🏨 Expedia",
            expedia_url,
            help="Book flights and hotels on Expedia",
            use_container_width=True
        )
    
    # Additional Indian platforms
    st.markdown("#### 🇮🇳 Popular Indian Platforms")
    col3, col4 = st.columns(2)
    
    with col3:
        makemytrip_url = f"https://www.makemytrip.com/flight/search?itinerary={from_param}-{to_param}-{date_str}&tripType=O&paxType=A-{passengers}_C-0_I-0&intl=false"
        st.link_button(
            "🎫 MakeMyTrip",
            makemytrip_url,
            help="Book on India's leading travel site",
            use_container_width=True
        )
    
    with col4:
        cleartrip_url = f"https://www.cleartrip.com/flights/results?from={from_param}&to={to_param}&depart_date={date_str}&adults={passengers}&children=0&infants=0&class=Economy&airline_pref=&sd=1567564200"
        st.link_button(
            "🎯 Cleartrip",
            cleartrip_url,
            help="Simple and transparent booking",
            use_container_width=True
        )

def display_price_chart(flights, from_city, to_city):
    """Display price comparison chart with better error handling"""
    try:
        prices = []
        airlines = []
        
        for f in flights:
            price_str = str(f.get("price", "0"))
            # Clean price string
            price_str = price_str.replace('₹', '').replace('$', '').replace('€', '').replace(',', '').replace(' ', '')
            price_match = re.search(r'\d+', price_str)
            
            if price_match:
                prices.append(int(price_match.group()))
                airline_name = f.get("airline", "Unknown")[:20]  # Truncate long names
                airlines.append(airline_name)
        
        if not prices or len(prices) < 2:
            return
            
        # Create the chart
        fig, ax = plt.subplots(figsize=(12, max(6, len(airlines) * 0.5)))
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        bar_colors = [colors[i % len(colors)] for i in range(len(airlines))]
        
        bars = ax.barh(airlines, prices, color=bar_colors)
        ax.set_xlabel("Price (₹)")
        ax.set_title(f"Price Comparison: {from_city} → {to_city}", fontsize=14, pad=20)
        
        # Add value labels on bars
        for bar, price in zip(bars, prices):
            width = bar.get_width()
            ax.text(width + max(prices) * 0.01, bar.get_y() + bar.get_height()/2, 
                   f'₹{price:,}', va='center', ha='left', fontweight='bold')
        
        # Improve layout
        ax.grid(axis='x', alpha=0.3)
        ax.set_axisbelow(True)
        plt.tight_layout()
        
        # Display chart
        st.pyplot(fig)
        plt.close()  # Close figure to prevent memory leaks
        
    except Exception as e:
        st.warning(f"Could not display price chart: {str(e)}")

def display_tips_and_info():
    """Display travel tips using native Streamlit components"""
    st.markdown("---")
    st.markdown("### 🌟 Flight Booking Tips")
    
    # Create tabs for different tip categories
    tip_tab1, tip_tab2, tip_tab3 = st.tabs(["💰 Save Money", "📅 Best Times", "✈️ Smart Booking"])
    
    with tip_tab1:
        st.write("**💡 Money-Saving Tips:**")
        money_tips = [
            "Book flights 2-8 weeks in advance for domestic, 2-6 months for international",
            "Clear browser cookies or use incognito mode to avoid price tracking",
            "Compare prices across multiple booking sites",
            "Consider nearby airports for potentially lower fares",
            "Sign up for airline newsletters and price alerts",
            "Use credit cards that offer travel rewards and protections"
        ]
        for tip in money_tips:
            st.write(f"• {tip}")
    
    with tip_tab2:
        st.write("**⏰ Best Booking Times:**")
        timing_tips = [
            "Tuesday and Wednesday departures are often cheapest",
            "Early morning and late night flights typically cost less",
            "Avoid peak travel seasons and holidays when possible",
            "Book domestic flights on Tuesday afternoons",
            "International flights: book on weekdays, fly on weekdays",
            "Red-eye flights can save 20-30% on ticket prices"
        ]
        for tip in timing_tips:
            st.write(f"• {tip}")
    
    with tip_tab3:
        st.write("**🎯 Smart Booking Strategies:**")
        booking_tips = [
            "Check airline websites directly after finding deals on aggregators",
            "Consider one-way tickets vs. round-trip for flexibility",
            "Look into budget airlines but factor in baggage fees",
            "Book refundable tickets if travel plans might change",
            "Check visa requirements and passport validity",
            "Read the fine print for cancellation and change policies"
        ]
        for tip in booking_tips:
            st.write(f"• {tip}")
    
    # Pro tip callout
    st.info("🔥 **Pro Tip:** Use Google Flights' price tracking feature to monitor fare changes for up to 2 months!")
    
    # Emergency contact info
    with st.expander("📞 Need Help?"):
        st.write("**If you encounter issues:**")
        st.write("• Contact the airline directly for booking changes")
        st.write("• Use travel insurance for unexpected cancellations")
        st.write("• Keep digital and physical copies of all travel documents")
        st.write("• Check airline apps for real-time updates and mobile boarding passes")