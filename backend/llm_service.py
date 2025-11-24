# backend/llm_service.py
import os
from langchain_groq import ChatGroq
from .config import config
from datetime import datetime, timedelta

class LLMService:
    def __init__(self):
        api_key = config.GROQ_API_KEY
        if not api_key:
            print("Warning: GROQ_API_KEY not found. Real AI generation will fail.")
            self.llm = None
        else:
            self.llm = ChatGroq(
                temperature=config.LLM_TEMPERATURE,
                model_name=config.GROQ_MODEL,
                groq_api_key=api_key
            )

    def generate_itinerary(self, prompt: str, start_date: str, end_date: str, context_data: dict) -> dict:
        """
        Generates a structured itinerary using Groq.
        """
        if not self.llm:
            return {
                "status": "error",
                "logs": ["GROQ_API_KEY missing"],
                "itinerary": [],
                "weather": context_data.get("weather", {}),
                "flights": context_data.get("flights", {}),
                "hotels": context_data.get("hotels", {}),
                "images": []
            }

        # Calculate number of days
        from datetime import datetime
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        num_days = (end_dt - start_dt).days + 1

        # Prepare context
        weather_summary = context_data.get("weather", {}).get("summary", "Unknown")
        weather_live = context_data.get("weather", {}).get("live", False)
        flights_live = context_data.get("flights", {}).get("live", False)
        flights_count = len(context_data.get("flights", {}).get("options", []))
        hotels_live = context_data.get("hotels", {}).get("live", False)
        hotels_count = len(context_data.get("hotels", {}).get("options", []))

        system_msg = """You are an expert travel planner. Create a detailed day-by-day itinerary.

IMPORTANT: Return ONLY a JSON array of days. Each day should have:
- day: number
- title: string (plain text, no markdown)
- summary: string
- schedule: array of {period, activity, duration, cost_estimate}
- cost_estimate: string (in INR)
- notes: array of strings

NO MARKDOWN. Use plain text only."""

        user_msg = f"""Create a {num_days}-day itinerary for: {prompt}
Dates: {start_date} to {end_date}
Weather: {weather_summary}

Return ONLY a JSON array like:
[{{"day": 1, "title": "Arrival", "summary": "...", "schedule": [{{"period": "Morning", "activity": "...", "duration": null, "cost_estimate": "₹500"}}], "cost_estimate": "₹2000", "notes": ["Tip 1"]}}]"""

        try:
            response = self.llm.invoke([
                ("system", system_msg),
                ("user", user_msg)
            ])
            
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse JSON
            import json
            import re
            
            # Try to extract JSON array
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                itinerary_days = json.loads(json_str)
            else:
                raise ValueError("No JSON array found in response")
            
            return {
                "status": "ok",
                "itinerary": itinerary_days,
                "weather": context_data.get("weather"),
                "flights": context_data.get("flights"),
                "hotels": context_data.get("hotels"),
                "images": [],
                "logs": [f"Generated {len(itinerary_days)} days"]
            }

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"LLM Error: {e}")
            print(error_details)
            return {
                "status": "error",
                "logs": [f"Error: {str(e)}"],
                "itinerary": [],
                "weather": context_data.get("weather", {}),
                "flights": context_data.get("flights", {}),
                "hotels": context_data.get("hotels", {}),
                "images": []
            }

# Singleton instance
llm_service = LLMService()
