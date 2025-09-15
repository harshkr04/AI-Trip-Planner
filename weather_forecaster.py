# agents/weather/weather_checker.py

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
import requests
import os
from dotenv import load_dotenv

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

def get_openmeteo_weather(destination, month):
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={destination}"
        geo = requests.get(geo_url).json()

        if 'results' not in geo:
            return "Location not found from Open-Meteo."

        lat = geo['results'][0]['latitude']
        lon = geo['results'][0]['longitude']

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current=temperature_2m,weathercode"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
            f"&timezone=auto"
        )
        weather_data = requests.get(weather_url).json()

        current = weather_data.get("current", {})
        daily = weather_data.get("daily", {})

        current_temp = current.get("temperature_2m", "N/A")
        max_temp = daily.get("temperature_2m_max", ["N/A"])[0]
        min_temp = daily.get("temperature_2m_min", ["N/A"])[0]
        rain = daily.get("precipitation_sum", ["N/A"])[0]

        return (
            f"📍 **Real-Time Weather (via Open-Meteo)**\n"
            f"- Current Temp: {current_temp}°C\n"
            f"- Max Temp: {max_temp}°C\n"
            f"- Min Temp: {min_temp}°C\n"
            f"- Precipitation: {rain} mm\n"
        )
    except Exception as e:
        return f"Failed to fetch Open-Meteo weather: {e}"

def weather_forecaster(state):
    destination = state['preferences'].get('destination', '')
    month = state['preferences'].get('month', '')

    realtime_weather = get_openmeteo_weather(destination, month)

    # Add Groq-based forecasting as "AI Forecast"
    try:
        llm = ChatGroq(model="llama3-8b-8192", temperature=0.1, api_key=groq_api_key)
        prompt = f"""
        Based on the destination and month, provide a smart weather forecast including travel advice:
        Destination: {destination}
        Month: {month}
        """
        ai_forecast = llm.invoke([HumanMessage(content=prompt)]).content.strip()
    except Exception as e:
        ai_forecast = f"AI forecast failed: {e}"

    return {
        "weather_forecast": f"{realtime_weather}\n\n🧠 **AI Travel Weather Advice:**\n{ai_forecast}"
    }
