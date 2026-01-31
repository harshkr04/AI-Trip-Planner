// frontend/src/pages/FlightSearch.jsx
import React, { useState } from "react";
import { searchFlights } from "../api/flights";
import Section from "../components/Section";
import DatePickerField from "../components/DatePickerField";

export default function FlightSearch() {
  const [origin, setOrigin] = useState("Delhi");
  const [destination, setDestination] = useState("Manali");
  const [date, setDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [flights, setFlights] = useState([]);
  const [error, setError] = useState("");
  const [cabinClass, setCabinClass] = useState("economy");
  const [currency, setCurrency] = useState("INR");
  const [tripType, setTripType] = useState("one-way");
  const [stops, setStops] = useState("any");
  const [maxPrice, setMaxPrice] = useState("");
  const [airlines, setAirlines] = useState("");

  const handleSearch = async () => {
    if (!origin || !destination || !date) {
      setError("Please fill origin, destination and date.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const res = await searchFlights({ 
        origin, 
        destination, 
        start_date: date,
        cabin_class: cabinClass,
        currency,
        trip_type: tripType,
        stops,
        max_price: maxPrice || undefined,
        airlines: airlines || undefined
      });
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

      <div style={{ display: "flex", gap: 12, marginTop: 12, marginBottom: 18, flexWrap: "wrap" }}>
        <input className="input" placeholder="Origin" value={origin} onChange={e => setOrigin(e.target.value)} style={{ width: 160 }} />
        <input className="input" placeholder="Destination" value={destination} onChange={e => setDestination(e.target.value)} style={{ width: 160 }} />
        <DatePickerField value={date} onChange={setDate} placeholder="Departure date" />
        <button className="btn-send" onClick={handleSearch} disabled={loading} style={{ minWidth: 140 }}>
          {loading ? "Searching..." : "Search Flights"}
        </button>
      </div>

      <Section title="Advanced Options" defaultOpen={false}>
        <div className="advanced-options-grid">
          <div className="advanced-field">
            <label>Cabin Class</label>
            <select className="input" value={cabinClass} onChange={e => setCabinClass(e.target.value)}>
              <option value="economy">Economy</option>
              <option value="premium">Premium Economy</option>
              <option value="business">Business</option>
              <option value="first">First Class</option>
            </select>
          </div>

          <div className="advanced-field">
            <label>Currency</label>
            <select className="input" value={currency} onChange={e => setCurrency(e.target.value)}>
              <option value="INR">INR (₹)</option>
              <option value="USD">USD ($)</option>
              <option value="EUR">EUR (€)</option>
            </select>
          </div>

          <div className="advanced-field">
            <label>Trip Type</label>
            <select className="input" value={tripType} onChange={e => setTripType(e.target.value)}>
              <option value="one-way">One-way</option>
              <option value="round-trip">Round-trip</option>
            </select>
          </div>

          <div className="advanced-field">
            <label>Stops</label>
            <select className="input" value={stops} onChange={e => setStops(e.target.value)}>
              <option value="any">Any</option>
              <option value="nonstop">Non-stop</option>
              <option value="1">1 Stop</option>
              <option value="2">2+ Stops</option>
            </select>
          </div>

          <div className="advanced-field">
            <label>Max Price</label>
            <input 
              className="input" 
              type="number" 
              placeholder="e.g. 10000" 
              value={maxPrice} 
              onChange={e => setMaxPrice(e.target.value)} 
            />
          </div>

          <div className="advanced-field">
            <label>Airlines (comma-separated)</label>
            <input 
              className="input" 
              placeholder="e.g. IndiGo, SpiceJet" 
              value={airlines} 
              onChange={e => setAirlines(e.target.value)} 
            />
          </div>
        </div>
      </Section>

      <Section title="Results" defaultOpen={true}>
        {error && <div className="empty">{error}</div>}
        {loading && flights.length === 0 ? (
          <div className="skeleton-list">
            {[1, 2, 3].map(i => (
              <div key={i} className="skeleton-row" />
            ))}
          </div>
        ) : flights.length === 0 ? (
          <div className="empty">No flights to show.</div>
        ) : (
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
