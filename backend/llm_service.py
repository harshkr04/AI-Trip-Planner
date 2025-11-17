# backend/llm_service.py
from datetime import datetime, timedelta
import re

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

    def generate_itinerary(self, prompt: str, start_date: str, end_date: str, context: str = ""):
        """
        Create a more detailed, date-aware itinerary text.
        This is a deterministic helper for demo/testing. Replace with real LLM call when ready.
        """
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
        out = []
        out.append(f"AI Trip Plan for: {prompt}")
        out.append(f"Destination: {destination}")
        out.append(f"Dates: {dstart.strftime('%Y-%m-%d')} to {dend.strftime('%Y-%m-%d')}")
        if context:
            out.append("")
            out.append("Context:")
            out.extend(line for line in context.splitlines()[:10])  # small context snippet
        if budget_text:
            out.append(budget_text)
        out.append("")
        # day-by-day
        for i in range(ndays):
            day_date = dstart + timedelta(days=i)
            out.append(f"## Day {i+1} — {day_date.strftime('%A, %d %b %Y')}")
            activities = self._mk_day_activity(i+1, destination, prompt)
            for t, desc in activities:
                out.append(f"- {t}: {desc}")
            # suggestion per day
            if i == 0:
                out.append(f"- Tip: Arrive early to settle in. Keep a light bag for first-day exploration.")
            if i == ndays - 1:
                out.append("- Departure: Keep travel time in mind and plan logistics early.")
            out.append("")  # blank line between days

        # additional suggestions
        out.append("## Packing & Practical Tips")
        out.append("- Carry a light rain jacket and comfortable shoes.")
        if "trek" in prompt.lower() or "hike" in prompt.lower():
            out.append("- Bring a small first-aid kit, trekking shoes, and sufficient water.")
        out.append("- Local transport: consider prepaid taxis or shared cabs for short distances.")
        out.append("")
        out.append("## Budget & Accommodation Notes")
        if budget and people:
            out.append(f"- Suggested: Look for hostels / budget hotels ₹{int(budget*0.4)}–₹{int(budget*0.7)} per night per person to remain within budget.")
        else:
            out.append("- Suggested: Book accommodation near the city centre / transport hub to save time.")
        out.append("")
        out.append("Enjoy your trip! This itinerary is a suggested plan — tweak it based on pace and preferences.")

        return "\n".join(out)

# single instance for import
llm_service = LLMService()
