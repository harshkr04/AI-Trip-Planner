// frontend/src/pages/HomePage.jsx
import React, { useState, useEffect } from "react";
import ItinerarySection from "../components/ItinerarySection";
import Section from "../components/Section";
import { createItinerary } from "../api/itinerary";

/**
 * HomePage now supports:
 * - selectedSession prop (object) -> loads its fields
 * - selectedSession === null         -> clears form for a new chat
 */
export default function HomePage({ sessions = [], saveSessions = () => {}, selectedSession = null }) {
  const [prompt, setPrompt] = useState("");
  const [origin, setOrigin] = useState("Delhi");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [loading, setLoading] = useState(false);

  const [itinerary, setItinerary] = useState("");
  const [weather, setWeather] = useState(null);
  const [flights, setFlights] = useState([]);
  const [hotels, setHotels] = useState([]);

  // When selectedSession becomes a real session object -> load it
  // When selectedSession becomes null/undefined -> clear form (new chat)
  useEffect(() => {
    if (selectedSession) {
      setPrompt(selectedSession.prompt || "");
      setOrigin(selectedSession.origin || "Delhi");
      setStart(selectedSession.start_date || "");
      setEnd(selectedSession.end_date || "");
      setItinerary(selectedSession.itinerary || "");
      setWeather(selectedSession.weather || null);
      setFlights(selectedSession.flights || []);
      setHotels(selectedSession.hotels || []);
      return;
    }

    // if selectedSession is null/undefined -> clear UI for a fresh "New Chat"
    setPrompt("");
    setOrigin("Delhi");
    setStart("");
    setEnd("");
    setItinerary("");
    setWeather(null);
    setFlights([]);
    setHotels([]);
  }, [selectedSession]);

  // Keep local storage in sync (optional)
  useEffect(() => {
    try {
      const raw = localStorage.getItem("ai_chat_sessions");
      if (raw) {
        // no action needed here — we keep sessions via props/saveSessions
      }
    } catch (e) {}
  }, []);

  const onSend = async () => {
    if (!prompt || !start || !end) return;
    setLoading(true);
    try {
      const data = await createItinerary({ prompt, start_date: start, end_date: end, origin });
      setItinerary(data.itinerary_text || "");
      setWeather(data.weather || null);
      setFlights(data.flights || []);
      setHotels(data.hotels || []);

      const session = {
        id: Date.now(),
        title: prompt.length > 40 ? `${prompt.substring(0, 37)}...` : prompt,
        createdAt: Date.now(),
        prompt,
        origin,
        start_date: start,
        end_date: end,
        itinerary: data.itinerary_text || "",
        weather: data.weather || null,
        flights: data.flights || [],
        hotels: data.hotels || []
      };
      const newSessions = [session, ...sessions].slice(0, 20);
      saveSessions(newSessions);
    } catch (e) {
      alert(e?.response?.data?.detail || e.message || "Error generating itinerary");
    }
    setLoading(false);
  };

  const weatherForRange = () => {
    if (!weather || !weather.days) return [];
    if (!start || !end) return weather.days;
    const from = new Date(start);
    const to = new Date(end);
    return weather.days.filter(d => {
      const dt = new Date(d.date);
      return dt >= from && dt <= to;
    });
  };

  return (
    <>
      <header className="hero">
        <div className="hero-icon">✈️</div>
        <h1 className="hero-title">AI Travel Assistant</h1>
        <p className="hero-subtitle">Let AI plan your perfect trip. Just describe your dream destination, pick your dates, and let us handle the rest—flights, hotels, weather, and a personalized day-by-day itinerary.</p>

        <div className="input-row" style={{ display: "flex", gap: 12, alignItems: "center", width: "100%" }}>
          <input className="input input-prompt" type="text" placeholder="e.g., Plan a 5-day Kerala trip..." value={prompt} onChange={e => setPrompt(e.target.value)} style={{ flex: 1 }} />
          <input className="input input-origin" type="text" placeholder="Origin (Delhi)" value={origin} onChange={e => setOrigin(e.target.value)} style={{ width: 140 }} />
          <input className="input input-date" type="date" value={start} onChange={e => setStart(e.target.value)} style={{ width: 160 }} />
          <input className="input input-date" type="date" value={end} onChange={e => setEnd(e.target.value)} style={{ width: 160 }} />
          <button className="btn-send" onClick={onSend} disabled={loading || !prompt || !start || !end} style={{ minWidth: 120 }}>
            {loading ? "Generating..." : "Send"}
          </button>
        </div>
      </header>

      <div className="sections">
        <ItinerarySection itinerary={itinerary} />
        <Section title="Weather Forecast" defaultOpen={false}>
          {!weather ? <div className="empty">No weather data yet.</div> : (
            <div>
              <div className="subtle">{weather.summary}</div>
              <div className="grid">
                {weatherForRange().map((d, i) => (
                  <div key={i} className="card-mini">
                    <div className="bold">{d.date}</div>
                    <div className="temp">{d.temp ?? d.temp_max ?? "-"}°C</div>
                    <div className="muted">{d.icon}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Section>

        <Section title="Flight Options" defaultOpen={false}>
          {flights.length === 0 ? <div className="empty">No flights available.</div> : (
            <div className="list">
              {flights.map((f, idx) => (
                <div key={idx} className="list-row">
                  <div className="chip">{f.airline}</div>
                  <div>{f.from} → {f.to}</div>
                  <div className="muted">{f.depart || "-"}</div>
                  <div className="price">₹{f.price}</div>
                </div>
              ))}
            </div>
          )}
        </Section>

        <Section title="Hotel Options" defaultOpen={false}>
          {hotels.length === 0 ? <div className="empty">No hotels available.</div> : (
            <div className="list">
              {hotels.map((h, idx) => (
                <div key={idx} className="list-row">
                  <div className="chip">{h.rating}★</div>
                  <div>{h.name}</div>
                  <div className="muted">{h.area || "-"}</div>
                  <div className="price">₹{h.price_per_night}/night</div>
                </div>
              ))}
            </div>
          )}
        </Section>
      </div>
    </>
  );
}
