// frontend/src/pages/FlightSearch.jsx
import React, { useState } from "react";
import { searchFlights } from "../api/flights";
import Section from "../components/Section";

export default function FlightSearch() {
  const [origin, setOrigin] = useState("Delhi");
  const [destination, setDestination] = useState("Manali");
  const [date, setDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [flights, setFlights] = useState([]);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    if (!origin || !destination || !date) {
      setError("Please fill origin, destination and date.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const res = await searchFlights({ origin, destination, start_date: date });
      const data = res.data || res; // backend may wrap
      setFlights(data.data || data || []);
    } catch (e) {
      console.error(e);
      setError("Failed to fetch flights.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={{ marginTop: 6 }}>Flight Search & Comparison</h2>

      <div style={{ display: "flex", gap: 12, marginTop: 12, marginBottom: 18 }}>
        <input className="input" placeholder="Origin" value={origin} onChange={e => setOrigin(e.target.value)} style={{ width: 160 }} />
        <input className="input" placeholder="Destination" value={destination} onChange={e => setDestination(e.target.value)} style={{ width: 160 }} />
        <input className="input input-date" type="date" value={date} onChange={e => setDate(e.target.value)} style={{ width: 160 }} />
        <button className="btn-send" onClick={handleSearch} disabled={loading} style={{ minWidth: 140 }}>
          {loading ? "Searching..." : "Search Flights"}
        </button>
      </div>

      <Section title="Results" defaultOpen={true}>
        {error && <div className="empty">{error}</div>}
        {flights.length === 0 ? <div className="empty">No flights to show.</div> : (
          <div className="list">
            {flights.map((f, idx) => (
              <div key={idx} className="list-row">
                <div className="chip">{f.airline}</div>
                <div>{f.from} → {f.to}</div>
                <div className="muted">{f.depart}</div>
                <div className="price">₹{f.price}</div>
              </div>
            ))}
          </div>
        )}
      </Section>
    </div>
  );
}
