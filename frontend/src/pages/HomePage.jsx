// frontend/src/pages/HomePage.jsx
import React, { useState, useEffect } from "react";
import ItinerarySection from "../components/ItinerarySection";
import Section from "../components/Section";
import DatePickerField from "../components/DatePickerField";
import { createItinerary, refineItinerary, saveDayNote } from "../api/itinerary";
import { downloadPdf, sharePdfByEmail } from "../api/pdf";

/**
 * HomePage now supports:
 * - selectedSession prop (object) -> loads its fields
 * - selectedSession === null         -> clears form for a new chat
 */
export default function HomePage({
  sessions = [],
  saveSessions = () => { },
  selectedSession = null,
  isDarkMode,
  toggleTheme
}) {
  const [prompt, setPrompt] = useState("");
  const [origin, setOrigin] = useState("Delhi");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [loading, setLoading] = useState(false);

  const [itineraryText, setItineraryText] = useState("");
  const [itineraryRich, setItineraryRich] = useState(null);
  const [weather, setWeather] = useState(null);
  const [flights, setFlights] = useState([]);
  const [hotels, setHotels] = useState([]);
  const [refineMessages, setRefineMessages] = useState([]);
  const [refineLoading, setRefineLoading] = useState(false);
  const [itineraryId, setItineraryId] = useState(null);
  const [savingNotes, setSavingNotes] = useState({});
  const [emailSending, setEmailSending] = useState(false);

  // When selectedSession becomes a real session object -> load it
  // When selectedSession becomes null/undefined -> clear form (new chat)
  const mapConversationToMessages = (conversation = []) =>
    conversation.map((msg, idx) => ({
      id: `${idx}-${msg.role}`,
      role: msg.role,
      content: msg.content,
    }));

  useEffect(() => {
    if (selectedSession) {
      setPrompt(selectedSession.prompt || "");
      setOrigin(selectedSession.origin || "Delhi");
      setStart(selectedSession.start_date || "");
      setEnd(selectedSession.end_date || "");
      const structured = selectedSession.itineraryRich || (typeof selectedSession.itinerary === "object" ? selectedSession.itinerary : null);
      setItineraryText(selectedSession.itinerary_text || (typeof selectedSession.itinerary === "string" ? selectedSession.itinerary : ""));
      setItineraryRich(structured);
      setItineraryId(selectedSession.itinerary_id || selectedSession.id || null);
      setWeather(selectedSession.weather || null);
      setFlights(selectedSession.flights || []);
      setHotels(selectedSession.hotels || []);
      setRefineMessages(mapConversationToMessages(selectedSession.refinements || []));
      return;
    }

    // if selectedSession is null/undefined -> clear UI for a fresh "New Chat"
    setPrompt("");
    setOrigin("Delhi");
    setStart("");
    setEnd("");
    setItineraryText("");
    setItineraryRich(null);
    setWeather(null);
    setFlights([]);
    setHotels([]);
    setRefineMessages([]);
    setItineraryId(null);
  }, [selectedSession]);

  // Keep local storage in sync (optional)
  useEffect(() => {
    try {
      const raw = localStorage.getItem("ai_chat_sessions");
      if (raw) {
        // no action needed here — we keep sessions via props/saveSessions
      }
    } catch (e) { }
  }, []);

  const onSend = async () => {
    if (!prompt || !start || !end) {
      alert("Please fill in all fields: prompt, start date, and end date.");
      return;
    }
    // Validate dates
    const startDate = new Date(start);
    const endDate = new Date(end);
    if (endDate <= startDate) {
      alert("End date must be after start date.");
      return;
    }
    setLoading(true);
    try {
      const data = await createItinerary({ prompt, start_date: start, end_date: end, origin });
      console.log("=== API Response Data ===");
      console.log("Full response:", data);
      console.log("itinerary object:", data.itinerary);
      console.log("itinerary.days:", data.itinerary?.days);
      console.log("itinerary.days length:", data.itinerary?.days?.length);
      setItineraryText(data.itinerary_text || "");
      setItineraryRich(data.itinerary || null);
      setItineraryId(data.itinerary_id || null);
      setWeather(data.weather || null);
      setFlights(data.flights || []);
      setHotels(data.hotels || []);
      setRefineMessages(mapConversationToMessages(data.conversation || []));

      const session = {
        id: Date.now(),
        title: prompt.length > 40 ? `${prompt.substring(0, 37)}...` : prompt,
        createdAt: Date.now(),
        prompt,
        origin,
        start_date: start,
        end_date: end,
        itinerary: data.itinerary_text || "",
        itinerary_text: data.itinerary_text || "",
        itineraryRich: data.itinerary || null,
        weather: data.weather || null,
        flights: data.flights || [],
        hotels: data.hotels || [],
        refinements: data.conversation || [],
        itinerary_id: data.itinerary_id || null,
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

  const handleDownloadPdf = async () => {
    if (!itineraryText) {
      alert("Generate an itinerary first.");
      return;
    }
    await downloadPdf({
      title: prompt ? `Trip: ${prompt}` : "Trip Itinerary",
      itinerary: itineraryText,
      itinerary_text: itineraryText,
      itinerary_days: itineraryRich?.days || [],
      destination: itineraryRich?.destination || "",
      cover_image: itineraryRich?.hero_image || "",
      summary: itineraryRich?.summary || "",
      overall_tips: itineraryRich?.overall_tips || itineraryRich?.overallTips || [],
    });
  };

  const handleShareEmail = async ({ to, subject, message }) => {
    if (!itineraryText) {
      alert("Generate an itinerary first.");
      return;
    }
    try {
      setEmailSending(true);
      await sharePdfByEmail({
        email: to,
        subject,
        message,
        itineraryPayload: {
          title: prompt ? `Trip: ${prompt}` : "Trip Itinerary",
          itinerary: itineraryText,
          itinerary_text: itineraryText,
          itinerary_days: itineraryRich?.days || [],
          destination: itineraryRich?.destination || "",
          cover_image: itineraryRich?.hero_image || "",
          summary: itineraryRich?.summary || "",
          overall_tips: itineraryRich?.overall_tips || [],
        },
      });
      alert("Itinerary emailed successfully!");
    } catch (error) {
      console.error(error);
      alert(error?.response?.data?.detail || "Unable to send email right now.");
    } finally {
      setEmailSending(false);
    }
  };

  const handleRefine = async (instruction) => {
    if (!itineraryRich || !itineraryId) {
      alert("Generate an itinerary first.");
      return;
    }
    const message = { id: Date.now(), role: "user", content: instruction };
    setRefineMessages((prev) => [...prev, message]);
    setRefineLoading(true);
    try {
      console.log("Refining itinerary with:", { itineraryId, instruction });
      const result = await refineItinerary({ itineraryId, instruction });
      console.log("Refine result:", result);

      if (result.itinerary) {
        setItineraryRich(result.itinerary);
      } else if (result.changed_days && result.changed_days.length > 0) {
        setItineraryRich((prev) => ({
          ...prev,
          days: mergeChangedDays(prev?.days || [], result.changed_days),
        }));
      }
      if (result.itinerary_text) {
        setItineraryText(result.itinerary_text);
      }
      if (result.conversation?.length) {
        setRefineMessages(mapConversationToMessages(result.conversation));
      } else {
        const assistantMsg = {
          id: Date.now() + 1,
          role: "assistant",
          content: result.message || "Plan updated with your instructions.",
        };
        setRefineMessages((prev) => [...prev, assistantMsg]);
      }
    } catch (error) {
      console.error("Refine error details:", {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        itineraryId,
        instruction
      });

      let errorMessage = "Couldn't refine right now. ";
      if (error.response?.status === 404) {
        errorMessage += "Itinerary not found. Please generate a new itinerary.";
      } else if (error.response?.status >= 500) {
        errorMessage += "Server error. Please try again in a moment.";
      } else if (error.message?.includes("Network Error") || !error.response) {
        errorMessage += "Network error. Check your connection and try again.";
      } else {
        errorMessage += "Try again shortly or rephrase your request.";
      }

      setRefineMessages((prev) => [
        ...prev,
        { id: Date.now() + 2, role: "assistant", content: errorMessage },
      ]);
    } finally {
      setRefineLoading(false);
    }
  };

  const mergeChangedDays = (days, patches) => {
    if (!days?.length) return days;
    return days.map((day) => {
      const patch = patches.find((p) => Number(p.day) === Number(day.day));
      return patch ? patch.data : day;
    });
  };

  const handleSaveNote = async (dayNumber, note) => {
    if (!itineraryId) {
      alert("Generate an itinerary first.");
      return;
    }
    setSavingNotes((prev) => ({ ...prev, [dayNumber]: true }));
    setItineraryRich((prev) => {
      if (!prev?.days) return prev;
      return {
        ...prev,
        days: prev.days.map((day) =>
          Number(day.day) === Number(dayNumber) ? { ...day, personal_note: note } : day
        ),
      };
    });
    try {
      await saveDayNote({ itineraryId, day: dayNumber, note });
    } catch (error) {
      alert("Unable to save note right now.");
    } finally {
      setSavingNotes((prev) => {
        const next = { ...prev };
        delete next[dayNumber];
        return next;
      });
    }
  };

  return (
    <>
      <header className="hero">
        <button
          className="theme-toggle-btn"
          onClick={toggleTheme}
          aria-label="Toggle Dark Mode"
          title={isDarkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
        >
          {isDarkMode ? "☀️" : "🌙"}
        </button>
        <div className="hero-grid">
          <div className="hero-copy">
            <span className="hero-badge">AI Travel Workspace</span>
            <h1 className="hero-title">
              Create a perfect trip <span>with our planner</span>
            </h1>
            <p className="hero-subtitle">
              Let intelligent travel advisors help you design bespoke adventures. From curated itineraries and real-time weather to on-budget flights and boutique stays, every detail is orchestrated in one elegant dashboard.
            </p>

            <div className="hero-stats">
              <div className="stat-card">
                <span className="stat-value">120+</span>
                <span className="stat-label">Destinations tracked</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">40K</span>
                <span className="stat-label">Saved itineraries</span>
              </div>
              <div className="stat-card">
                <span className="stat-value">24/7</span>
                <span className="stat-label">Weather + alerts</span>
              </div>
            </div>
          </div>

          <div className="hero-media" aria-hidden="true">
            <div className="hero-photo" />
            <div className="hero-overlay-card">
              <div className="mini-card">
                <div className="mini-title">Mountain Escape</div>
                <div className="mini-chip">Kerala • 5 days</div>
              </div>
              <div className="mini-card">
                <div className="mini-title">Coastline Drive</div>
                <div className="mini-chip">Goa • 3 days</div>
              </div>
              <div className="mini-card">
                <div className="mini-title">Endless Forests</div>
                <div className="mini-chip">Himachal • 7 days</div>
              </div>
            </div>
          </div>
        </div>

        <div className="hero-form">
          <div className="hero-form-head">
            <div>
              <span style={{ opacity: 0.7, fontSize: 13 }}>Trip builder</span>
              <strong>Describe your next getaway</strong>
            </div>
            <span style={{ fontSize: 13, opacity: 0.75 }}>Flights, stays, weather & PDF in one click</span>
          </div>
          <form
            className="input-row"
            onSubmit={(e) => {
              e.preventDefault();
              onSend();
            }}
          >
            <input
              className="input input-prompt"
              type="text"
              placeholder="E.g. Plan a 5-day Kerala wellness retreat"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
            <input
              className="input input-origin"
              type="text"
              placeholder="Origin city"
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
            />
            <DatePickerField className="input-date" value={start} onChange={setStart} placeholder="Start date" />
            <DatePickerField className="input-date" value={end} onChange={setEnd} placeholder="End date" />
            <button className="btn-send" type="submit" disabled={loading || !prompt || !start || !end}>
              {loading ? "Generating..." : "Build Plan"}
            </button>
          </form>
        </div>
      </header>

      <div className="sections">
        <ItinerarySection
          itinerary={itineraryRich}
          itineraryText={itineraryText}
          onDownloadPdf={handleDownloadPdf}
          onShareEmail={handleShareEmail}
          emailSending={emailSending}
          refineMessages={refineMessages}
          onRefine={handleRefine}
          refineLoading={refineLoading}
          onSaveNote={handleSaveNote}
          savingNotes={savingNotes}
        />
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
