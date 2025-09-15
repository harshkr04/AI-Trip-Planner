# pages/main_travel_page.py - Main Travel Planning Page

import streamlit as st
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_community.tools.google_serper import GoogleSerperAPIWrapper

import datetime
import os
from agents import (
    generate_itinerary,
    recommend_activities,
    fetch_useful_links,
    weather_forecaster,
    packing_list_generator,
    food_culture_recommender,
    chat_agent,
    budget_estimator,
    currency_converter,
    attractions_finder
)
from utils_export import export_to_pdf

def render():
    """Render the main travel planning page"""
    
    # Get API keys
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    # Initialize LLM
    try:
        llm = ChatGroq(model="llama3-8b-8192", temperature=0.1, api_key=groq_api_key)
    except Exception as e:
        st.error(f"LLM initialization failed: {str(e)}")
        st.stop()

    # Initialize Google Search API
    try:
        search = GoogleSerperAPIWrapper()
    except Exception as e:
        st.error(f"Serper API initialization failed: {str(e)}")
        st.stop()

    # ------------------- State -------------------
    class GraphState(TypedDict):
        preferences_text: str
        preferences: dict
        itinerary: str
        activity_suggestions: str
        useful_links: list[dict]
        weather_forecast: str
        packing_list: str
        food_culture_info: str
        chat_history: Annotated[list[dict], "List of question-response pairs"]
        user_question: str
        chat_response: str
        flight_prices: list[dict]

    # ------------------- LangGraph -------------------
    workflow = StateGraph(GraphState)
    workflow.add_node("generate_itinerary", generate_itinerary.generate_itinerary)
    workflow.set_entry_point("generate_itinerary")
    workflow.add_edge("generate_itinerary", END)
    graph = workflow.compile()

    # ------------------- UI -------------------
    st.markdown("# 🌟 AI-Powered Travel Itinerary Planner")
    st.markdown("### Plan your perfect trip with AI assistance")

    if "state" not in st.session_state:
        st.session_state.state = {
            "preferences_text": "",
            "preferences": {},
            "itinerary": "",
            "activity_suggestions": "",
            "useful_links": [],
            "weather_forecast": "",
            "packing_list": "",
            "food_culture_info": "",
            "chat_history": [],
            "user_question": "",
            "chat_response": "",
            "flight_prices": []
        }

    # Travel Form
    with st.form("travel_form"):
        st.markdown("## 📝 Trip Details")
        
        col1, col2 = st.columns(2)
        with col1:
            From = st.text_input("From (Starting Point)", 
                               placeholder="e.g., Delhi, Mumbai", 
                               help="Enter city or location name")
            destination = st.text_input("Destination", 
                                      placeholder="e.g., Goa, Manali", 
                                      help="Enter destination city")

            from_date = st.date_input("From Date", min_value=datetime.date.today())
            to_date = st.date_input("To Date", min_value=from_date)

            month = from_date.strftime("%B") if from_date else "Unknown"
            num_people = st.selectbox("Number of People", ["1", "2", "3", "4-6", "7-10", "10+"])
            
        with col2:
            holiday_type = st.selectbox(
                "Holiday Type",
                ["Any", "Party", "Skiing", "Backpacking", "Family", "Beach",
                 "Festival", "Adventure", "City Break", "Romantic", "Cruise"]
            )
            budget_type = st.selectbox(
                "Budget Type",
                ["Budget", "Mid-Range", "Luxury", "Backpacker", "Family"]
            )
            comments = st.text_area("Additional Comments", 
                                  placeholder="Any specific preferences, requirements, or activities you want to include...")
            
        submit_btn = st.form_submit_button("🚀 Generate Itinerary", type="primary")

    # Handle form submission
    if submit_btn:
        if not destination:
            st.error("❌ Please enter a destination!")
            return
            
        preferences_text = (
            f"Destination: {destination}\nFrom Date: {from_date}\nTo Date: {to_date}\n"
            f"People: {num_people}\nType: {holiday_type}\nBudget: {budget_type}\nComments: {comments}"
        )

        preferences = {
            "From": From,
            "destination": destination,
            "from_date": str(from_date),
            "to_date": str(to_date),
            "month": month,
            "num_people": num_people,
            "holiday_type": holiday_type,
            "budget_type": budget_type,
            "comments": comments
        }

        st.session_state.state.update({
            "preferences_text": preferences_text,
            "preferences": preferences,
            "chat_history": [],
            "user_question": "",
            "chat_response": "",
            "activity_suggestions": "",
            "useful_links": [],
            "weather_forecast": "",
            "packing_list": "",
            "food_culture_info": "",
            "flight_prices": []
        })
        
        with st.spinner("🔮 AI is crafting your perfect itinerary..."):
            result = graph.invoke(st.session_state.state)
            st.session_state.state.update(result)
            if result.get("itinerary"):
                st.success("✅ Itinerary Created Successfully!")
            else:
                st.error("❌ Failed to generate itinerary.")

    # Display Itinerary & Tools
    if st.session_state.state.get("itinerary"):
        st.markdown("---")
        
        col_itin, col_chat = st.columns([3, 2])

        with col_itin:
            st.markdown("## 📋 Your Travel Itinerary")
            st.markdown(st.session_state.state["itinerary"])

            st.markdown("### 🛠️ Additional Tools")
            
            # Primary action buttons
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button("🎯 Activity Suggestions", use_container_width=True):
                    with st.spinner("Fetching activity suggestions..."):
                        result = recommend_activities.recommend_activities(st.session_state.state)
                        st.session_state.state.update(result)
                        
            with col_btn2:
                if st.button("🌤️ Weather Forecast", use_container_width=True):
                    with st.spinner("Fetching weather forecast..."):
                        result = weather_forecaster.weather_forecaster(st.session_state.state)
                        st.session_state.state.update(result)
                        
            with col_btn3:
                if st.button("🎒 Packing List", use_container_width=True):
                    with st.spinner("Generating packing list..."):
                        result = packing_list_generator.packing_list_generator(st.session_state.state)
                        st.session_state.state.update(result)

            # Secondary action buttons
            col_btn4, col_btn5, col_btn6 = st.columns(3)
            with col_btn4:
                if st.button("🔗 Useful Links", use_container_width=True):
                    with st.spinner("Fetching useful links..."):
                        result = fetch_useful_links.fetch_useful_links(st.session_state.state)
                        st.session_state.state.update(result)
                        
            with col_btn5:
                if st.button("🍽️ Food & Culture", use_container_width=True):
                    with st.spinner("Fetching food and culture info..."):
                        result = food_culture_recommender.food_culture_recommender(st.session_state.state)
                        st.session_state.state.update(result)
                        
            with col_btn6:
                if st.button("🏛️ Nearby Attractions", use_container_width=True):
                    result = attractions_finder.get_attractions(st.session_state.state["preferences"].get("destination", ""))
                    st.session_state.state.update(result)

            # Financial tools
            col_btn7, col_btn8, col_btn9 = st.columns(3)
            with col_btn7:
                if st.button("💰 Budget Estimate", use_container_width=True):
                    result = budget_estimator.estimate_budget(st.session_state.state)
                    st.session_state.state.update(result)
                    
            with col_btn8:
                if st.button("💱 Currency Info", use_container_width=True):
                    result = currency_converter.get_currency_info(st.session_state.state)
                    st.session_state.state.update(result)
                    
            with col_btn9:
                # Flight search navigation button
                if st.button("✈️ Check Flight Prices", type="primary", use_container_width=True):
                    st.session_state.current_page = "flight_search"
                    st.rerun()

            # Export options
            st.markdown("### 📄 Export Options")
            col_export1, col_export2 = st.columns(2)
            with col_export1:
                if st.button("📄 Export as PDF", use_container_width=True):
                    pdf_path = export_to_pdf(st.session_state.state["itinerary"])
                    if pdf_path:
                        with open(pdf_path, "rb") as f:
                            st.download_button("⬇️ Download PDF", f, file_name="itinerary.pdf")
            
            with col_export2:
                st.download_button(
                    "💾 Download as Text",
                    st.session_state.state["itinerary"],
                    file_name=f"itinerary_{st.session_state.state['preferences'].get('destination', 'trip')}.txt"
                )

            # Display results in expandable sections
            display_results()

        # Chat Section
        with col_chat:
            st.markdown("### 💬 Chat About Your Trip")
            
            # Display chat history
            chat_container = st.container()
            with chat_container:
                for chat in st.session_state.state["chat_history"]:
                    with st.chat_message("user"):
                        st.markdown(chat["question"])
                    with st.chat_message("assistant"):
                        st.markdown(chat["response"])

            # Chat input
            if user_input := st.chat_input("Ask anything about your itinerary..."):
                st.session_state.state["user_question"] = user_input
                with st.spinner("Thinking..."):
                    result = chat_agent.chat_node(st.session_state.state)
                    st.session_state.state.update(result)
                    st.rerun()
    else:
        # Welcome message when no itinerary exists
        st.markdown("---")
        st.info("👆 Fill out the form above to generate your personalized travel itinerary!")
        
        # Sample destinations
        st.markdown("### 🌟 Popular Destinations")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**🏖️ Beach Destinations**\n- Goa\n- Kerala\n- Andaman")
        with col2:
            st.markdown("**🏔️ Mountain Destinations**\n- Manali\n- Shimla\n- Darjeeling")
        with col3:
            st.markdown("**🏛️ Cultural Destinations**\n- Rajasthan\n- Delhi\n- Agra")

def display_results():
    """Display all the generated results in expandable sections"""
    
    if st.session_state.state.get("activity_suggestions"):
        with st.expander("🎯 Activity Suggestions", expanded=False):
            st.markdown(st.session_state.state["activity_suggestions"])

    if st.session_state.state.get("useful_links"):
        with st.expander("🔗 Useful Links", expanded=False):
            for link in st.session_state.state["useful_links"]:
                st.markdown(f"• [{link['title']}]({link['url']})")

    if st.session_state.state.get("weather_forecast"):
        with st.expander("🌤️ Weather Forecast", expanded=False):
            st.markdown(st.session_state.state["weather_forecast"])

    if st.session_state.state.get("packing_list"):
        with st.expander("🎒 Packing List", expanded=False):
            st.markdown(st.session_state.state["packing_list"])

    if st.session_state.state.get("food_culture_info"):
        with st.expander("🍽️ Food & Culture", expanded=False):
            st.markdown(st.session_state.state["food_culture_info"])