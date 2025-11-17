# backend/services/weather_service.py
import requests
from ..config import config
from datetime import datetime, timedelta
from collections import defaultdict
import math

def _date_str(dt):
    return dt.strftime("%Y-%m-%d")

def _ensure_date_range(days_list, start_date, end_date):
    """
    Guarantee an entry for every date between start_date and end_date (inclusive).
    If API returned fewer days, fill with placeholders.
    """
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    ndays = (end - start).days + 1
    result = []
    existing = {d["date"][:10]: d for d in days_list}  # keyed by yyyy-mm-dd
    for i in range(ndays):
        cur = start + timedelta(days=i)
        key = _date_str(cur)
        if key in existing:
            result.append(existing[key])
        else:
            result.append({
                "date": cur.strftime("%Y-%m-%d"),
                "temp_min": None,
                "temp_max": None,
                "temp": None,
                "icon": "Unknown",
                "humidity": None
            })
    return result

def get_weather_for_trip(trip: dict):
    """
    Calls OpenWeather 5-day / 3-hour forecast and aggregates into per-day summary.
    Expects trip to contain 'destination', and optionally 'start_date' and 'end_date'.
    """
    destination = trip.get("destination", "Delhi")
    api_key = config.WEATHER_API_KEY
    if not api_key:
        # no key configured — return simple placeholder for each day in range
        start = trip.get("start_date")
        end = trip.get("end_date")
        if not start or not end:
            return {"summary": "Weather unavailable (no API key)", "days": []}
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        days = []
        for i in range((end_dt - start_dt).days + 1):
            cur = start_dt + timedelta(days=i)
            days.append({
                "date": cur.strftime("%Y-%m-%d"),
                "temp": None,
                "temp_min": None,
                "temp_max": None,
                "icon": "Unavailable",
                "humidity": None
            })
        return {"summary": "Weather API key not configured", "days": days}

    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": destination,
        "appid": api_key,
        "units": "metric",
    }
    try:
        r = requests.get(base_url, params=params, timeout=8)
        data = r.json()
        if "list" not in data:
            return {"summary": "Weather unavailable", "days": []}

        # aggregate by date
        by_date = defaultdict(list)
        for entry in data.get("list", []):
            dt_txt = entry.get("dt_txt")  # like "2025-11-25 12:00:00"
            if not dt_txt:
                continue
            date_key = dt_txt.split(" ")[0]
            by_date[date_key].append(entry)

        days = []
        for date_key, entries in sorted(by_date.items())[:10]:
            temps = [e.get("main", {}).get("temp") for e in entries if e.get("main", {}).get("temp") is not None]
            temp_mins = [e.get("main", {}).get("temp_min") for e in entries if e.get("main", {}).get("temp_min") is not None]
            temp_maxs = [e.get("main", {}).get("temp_max") for e in entries if e.get("main", {}).get("temp_max") is not None]
            humidities = [e.get("main", {}).get("humidity") for e in entries if e.get("main", {}).get("humidity") is not None]
            icon_counts = {}
            for e in entries:
                w = e.get("weather", [{}])[0].get("main", "Unknown")
                icon_counts[w] = icon_counts.get(w, 0) + 1
            # choose most common icon
            icon = max(icon_counts.items(), key=lambda x: x[1])[0] if icon_counts else "Unknown"

            day = {
                "date": date_key,
                "temp": round(sum(temps)/len(temps), 1) if temps else None,
                "temp_min": round(min(temp_mins), 1) if temp_mins else None,
                "temp_max": round(max(temp_maxs), 1) if temp_maxs else None,
                "icon": icon,
                "humidity": int(sum(humidities)/len(humidities)) if humidities else None
            }
            days.append(day)

        # ensure we have for full trip range if start/end provided
        start_date = trip.get("start_date")
        end_date = trip.get("end_date")
        if start_date and end_date:
            days = _ensure_date_range(days, start_date, end_date)

        summary = ""
        if days and days[0].get("temp") is not None:
            first = days[0]
            summary = f"{first['temp']}°C, {first['icon']}, {first.get('humidity', '')}% humidity"
        else:
            summary = "Weather retrieved (summary unavailable)"

        return {"summary": summary, "days": days}

    except Exception as e:
        # safe fallback
        return {"summary": "Weather unavailable", "days": []}
