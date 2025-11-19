# backend/llm_service.py
from datetime import datetime, timedelta
import re
from itertools import cycle

ACTIVITY_THEMES = [
    "Slow travel & discovery",
    "Culture and craft immersion",
    "Outdoor escapes & vistas",
    "Food trails & hidden cafes",
    "Wellness and mindful pauses",
]

TRANSPORT_MODES = [
    "10 min tuk-tuk ride",
    "15 min cab from city centre",
    "20 min seaside walk",
    "25 min metro hop",
    "30 min scenic drive",
]

FOOD_SUGGESTIONS = [
    "filter coffee & masala dosa",
    "fresh coconut water & poha",
    "street-side chaat & jalebi",
    "tandoori platter & craft beer",
    "local thali with seasonal sweets",
    "seafood grill with kokum soda",
]

TRAVEL_TIPS = [
    "Buffer 15 mins for traffic near popular spots.",
    "Keep digital copies of tickets & IDs.",
    "Carry small cash for local markets.",
    "Use ride-hailing apps during late evenings.",
    "Pack a reusable water bottle & stay hydrated.",
]

SAFETY_TIPS = [
    "Stick to well-lit streets after dark.",
    "Use hotel safe for passports and cash.",
    "Share live location when venturing out solo.",
    "Use licensed operators for adventure sports.",
    "Keep emergency numbers saved on phone.",
]

BUDGET_TIPS = [
    "Bundle attractions with city passes to save 20%.",
    "Opt for shared transfers for airport-city legs.",
    "Dine at lunchtime for chef menus at lower prices.",
    "Leverage local markets for souvenirs instead of malls.",
    "Pre-book ferries or mountain permits online.",
]

NIGHTLIFE_SUGGESTIONS = [
    "Jazz bar crawl",
    "Craft cocktail class",
    "Night bazaar tasting trail",
    "Beach-front DJ set",
    "Skyline rooftop lounge",
]

RELAX_SUGGESTIONS = [
    "Ayurvedic massage appointment",
    "Boutique spa soak",
    "Guided breathwork by the shore",
    "Slow brunch with ocean view",
    "Sunset meditation on the deck",
]

class LLMService:
    def _parse_budget_and_people(self, prompt: str):
        # try to extract patterns like "budget 4000", "4000 per person", "for 3 people"
        budget = None
        people = None
        m_budget = re.search(r"\b(?:budget|budget:?)\s*([₹$]?\d{3,})", prompt, re.IGNORECASE)
        if not m_budget:
            m_budget = re.search(r"\b([₹$]?\d{3,})\s*(?:per person|each|pp)\b", prompt, re.IGNORECASE)
        if m_budget:
            try:
                budget = int(re.sub(r"[^\d]", "", m_budget.group(1)))
            except:
                budget = None

        m_people = re.search(r"\b(?:for|of)?\s*(\d{1,2})\s*(?:people|persons|person|guests)\b", prompt, re.IGNORECASE)
        if m_people:
            try:
                people = int(m_people.group(1))
            except:
                people = None

        return budget, people

    def _mk_day_activity(self, day_index: int, destination: str, prompt: str):
        # create varied activities based on day index and prompt keywords
        base_activities = [
            ("Morning", f"Arrive {destination if day_index==1 else 'at your hotel'}, check-in and breakfast."),
            ("Afternoon", "Local sightseeing — visit main attractions and a recommended viewpoint."),
            ("Evening", "Enjoy local cuisine at a suggested cafe or market.")
        ]
        # modify based on keywords
        p = prompt.lower()
        if "trek" in p or "trekking" in p or "hike" in p:
            base_activities = [
                ("Morning", "Short trek / easy trail to warm up and enjoy scenery."),
                ("Afternoon", "Packed lunch and scenic exploration or waterfall visit."),
                ("Evening", "Relax at the hostel or local café; recover.")
            ]
        elif "beach" in p or "swim" in p:
            base_activities = [
                ("Morning", "Beach time: swim or walk along the shore."),
                ("Afternoon", "Explore local seafood and beach activities."),
                ("Evening", "Beach sunset and a relaxed dinner.")
            ]
        elif "food" in p or "cuisine" in p:
            base_activities[1] = ("Afternoon", "Culinary trail: try recommended local specialities and cafes.")
            base_activities[2] = ("Evening", "Visit a popular local restaurant for dinner.")
        # small variation:
        if day_index % 2 == 0:
            base_activities.insert(1, ("Midday", "Short café break and light shopping or museum visit."))

        return base_activities

    def _destination_photo(self, destination: str):
        library = {
            "goa": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&w=1600&q=70",
            "kerala": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&w=1600&q=70",
            "delhi": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&w=1600&q=70",
            "jaipur": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&w=1600&q=70",
            "manali": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&w=1600&q=70",
            "mumbai": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&w=1600&q=70",
            "ladakh": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&w=1600&q=70",
        }
        for key, url in library.items():
            if key in destination.lower():
                return url
        return "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&w=1600&q=70"

    def _segment_food(self, destination: str, seed: int):
        return f"Try {FOOD_SUGGESTIONS[seed % len(FOOD_SUGGESTIONS)]} near {destination}'s old town."

    def _segment_tip(self, seed: int):
        return TRAVEL_TIPS[seed % len(TRAVEL_TIPS)]

    def _safety_tip(self, seed: int):
        return SAFETY_TIPS[seed % len(SAFETY_TIPS)]

    def _budget_tip(self, seed: int):
        return BUDGET_TIPS[seed % len(BUDGET_TIPS)]

    def _weather_note(self, weather_day, default="Pleasant skies; carry light layers."):
        if not weather_day:
            return default
        icon = weather_day.get("icon") or ""
        temp = weather_day.get("temp") or weather_day.get("temp_max")
        summary = weather_day.get("summary") or weather_day.get("condition") or ""
        pieces = []
        if temp:
            pieces.append(f"{temp}°C")
        if icon:
            pieces.append(icon)
        if summary:
            pieces.append(summary)
        if not pieces:
            return default
        return " • ".join(pieces)

    def render_plan_text(self, plan: dict) -> str:
        """
        Convert structured plan into the legacy markdown-ish text format
        used by PDF + older UI pieces.
        """
        if not plan:
            return ""
        lines = []
        lines.append(plan.get("title", "AI Trip Plan"))
        range_meta = plan.get("date_range", {})
        if range_meta:
            lines.append(f"Dates: {range_meta.get('start')} to {range_meta.get('end')}")
        lines.append(f"Destination: {plan.get('destination', 'Your trip')}")
        if plan.get("summary"):
            lines.append(plan["summary"])
        lines.append("")
        for day in plan.get("days", []):
            lines.append(f"## Day {day.get('day')} — {day.get('date')} | {day.get('headline')}")
            if day.get("highlights"):
                lines.append(day["highlights"])
            for seg in day.get("segments", []):
                lines.append(f"- {seg['period']}: {seg['activity']} ({seg['food']})")
                if seg.get("tips"):
                    lines.append(f"  Tip: {seg['tips'][0]}")
            if day.get("travel_time"):
                lines.append(f"- Travel time: {day['travel_time']}")
            if day.get("weather_note"):
                lines.append(f"- Weather: {day['weather_note']}")
            if day.get("safety_tip"):
                lines.append(f"- Safety: {day['safety_tip']}")
            if day.get("budget_tip"):
                lines.append(f"- Budget: {day['budget_tip']}")
            if day.get("notes"):
                for note in day["notes"]:
                    lines.append(f"- Note: {note}")
            lines.append("")
        if plan.get("overall_tips"):
            lines.append("## Overall Travel Tips")
            for tip in plan["overall_tips"]:
                lines.append(f"- {tip}")
            lines.append("")
        if plan.get("food_spots"):
            lines.append("## Food & Drink Suggestions")
            for spot in plan["food_spots"]:
                lines.append(f"- {spot}")
            lines.append("")
        if plan.get("safety_notes"):
            lines.append("## Safety & Budget Notes")
            for note in plan["safety_notes"]:
                lines.append(f"- {note}")
        return "\n".join(lines)

    def generate_itinerary(self, prompt: str, start_date: str, end_date: str, context: str = "", weather_days=None):
        """
        Create a more detailed, date-aware itinerary text.
        This is a deterministic helper for demo/testing. Replace with real LLM call when ready.
        """
        weather_days = weather_days or []
        # parse dates
        try:
            dstart = datetime.fromisoformat(start_date)
        except Exception:
            dstart = datetime.now()
        try:
            dend = datetime.fromisoformat(end_date)
        except Exception:
            dend = dstart + timedelta(days=2)

        # ensure start <= end
        if dend < dstart:
            dend = dstart + timedelta(days=2)

        ndays = (dend - dstart).days + 1
        destination = None
        # try to extract explicit "to <city>" or capitalized word
        m_to = re.search(r"\bto\s+([A-Za-z ]{2,30})", prompt, re.IGNORECASE)
        if m_to:
            destination = m_to.group(1).strip().title()
        if not destination:
            # fallback to context or 'your destination'
            m_ctx = re.search(r"Destination:\s*([A-Za-z ]{2,30})", context or "", re.IGNORECASE)
            if m_ctx:
                destination = m_ctx.group(1).strip().title()
        destination = destination or "your destination"

        # budget & people
        budget, people = self._parse_budget_and_people(prompt)
        budget_text = ""
        if budget:
            if people and people > 0:
                total = budget * people
                budget_text = f"\nEstimated budget: ₹{budget} per person — approx ₹{total} total for {people} people."
            else:
                budget_text = f"\nEstimated budget: ₹{budget} (total / per person depending on prompt)."

        # header
        plan = {
            "title": f"AI Trip Plan for {destination}",
            "prompt": prompt,
            "destination": destination,
            "date_range": {"start": dstart.strftime("%Y-%m-%d"), "end": dend.strftime("%Y-%m-%d")},
            "summary": f"A {ndays}-day curated loop balancing discovery, downtime, and local flavour.",
            "context": context,
            "days": [],
            "overall_tips": [],
            "food_spots": [],
            "safety_notes": [],
            "budget_tips": [],
            "hero_image": self._destination_photo(destination),
        }

        activity_theme_iter = cycle(ACTIVITY_THEMES)
        transport_iter = cycle(TRANSPORT_MODES)

        for i in range(ndays):
            day_date = dstart + timedelta(days=i)
            weather_day = weather_days[i] if i < len(weather_days) else None
            headline = next(activity_theme_iter)
            travel_time = next(transport_iter)
            daily_food = self._segment_food(destination, i)
            day_plan = {
                "day": i + 1,
                "date": day_date.strftime("%A, %d %b %Y"),
                "headline": headline,
                "highlights": f"Focus on {headline.lower()} with curated stops.",
                "segments": [],
                "travel_time": travel_time,
                "local_food": daily_food,
                "weather_note": self._weather_note(weather_day),
                "safety_tip": self._safety_tip(i),
                "budget_tip": self._budget_tip(i),
                "notes": [],
            }
            activities = self._mk_day_activity(i+1, destination, prompt)
            for t, desc in activities:
                seg = {
                    "period": t,
                    "activity": desc,
                    "food": self._segment_food(destination, i + len(day_plan["segments"])),
                    "tips": [self._segment_tip(i + len(day_plan["segments"]))],
                    "travel_time": travel_time,
                }
                if t.lower() == "evening":
                    seg["tips"].append("Book ahead for popular dining rooms.")
                day_plan["segments"].append(seg)
            if i == 0:
                day_plan["notes"].append("Arrive early, keep ID handy for hotel check-in.")
            if i == ndays - 1:
                day_plan["notes"].append("Plan departure transfers with 90 min buffer.")
            plan["days"].append(day_plan)

        plan["overall_tips"] = [
            "Blend guided tours with self-exploration for balance.",
            "Confirm adventure activities 24h in advance.",
            "Carry a lightweight daypack for sudden showers.",
        ]
        if "trek" in prompt.lower() or "hike" in prompt.lower():
            plan["overall_tips"].append("Pack moisture-wicking layers and trekking poles.")
        plan["food_spots"] = [
            f"{destination} night food market for late bites.",
            "Chef-led tasting menu at a boutique restaurant.",
            "Sunset rooftop with mocktails overlooking the skyline.",
        ]
        plan["safety_notes"] = SAFETY_TIPS[:3]
        plan["budget_tips"] = BUDGET_TIPS[:3]
        if budget_text:
            plan["budget_tips"].append(budget_text.replace("\n", " ").strip())

        rendered_text = self.render_plan_text(plan)
        plan["rendered_text"] = rendered_text

        return {"text": rendered_text, "plan": plan}

# single instance for import
llm_service = LLMService()
