// frontend/src/pages/HotelSearch.jsx
import React, { useState } from "react";
import { searchHotels } from "../api/hotels";
import Section from "../components/Section";
import DatePickerField from "../components/DatePickerField";

export default function HotelSearch() {
  const [destination, setDestination] = useState("Manali");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [loading, setLoading] = useState(false);
  const [hotels, setHotels] = useState([]);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    if (!destination || !start || !end) {
      setError("Please fill destination and date range.");
      return;
    }
    // Validate dates
    const startDate = new Date(start);
    const endDate = new Date(end);
    if (endDate <= startDate) {
      setError("Check-out date must be after check-in date.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const res = await searchHotels({ destination, start_date: start, end_date: end });
      const data = res.data || res;
      setHotels(data || []);
    } catch (e) {
      console.error(e);
      setError("Failed to fetch hotels.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2 style={{ marginTop: 6 }}>Hotels & Comparison</h2>

      <div style={{ display: "flex", gap: 12, marginTop: 12, marginBottom: 18 }}>
        <input className="input" placeholder="Destination" value={destination} onChange={e => setDestination(e.target.value)} style={{ width: 160 }} />
        <DatePickerField value={start} onChange={setStart} placeholder="Check-in" />
        <DatePickerField value={end} onChange={setEnd} placeholder="Check-out" />
        <button className="btn-send" onClick={handleSearch} disabled={loading} style={{ minWidth: 140 }}>
          {loading ? "Searching..." : "Search Hotels"}
        </button>
      </div>

      <Section title="Results" defaultOpen={true}>
        {error && <div className="empty">{error}</div>}
        {loading && hotels.length === 0 ? (
          <div className="skeleton-list">
            {[1, 2, 3].map(i => (
              <div key={i} className="skeleton-row" />
            ))}
          </div>
        ) : hotels.length === 0 ? (
          <div className="empty">No hotels to show.</div>
        ) : (
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
  );
}
