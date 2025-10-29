import React, { useState } from "react";
import Sidebar from "./components/Sidebar";
import FlightsSection from "./components/FlightsSection";
import HotelsSection from "./components/HotelsSection";
import WeatherSection from "./components/WeatherSection";

import { getItinerary } from "./api/itinerary";
import { fetchFlights } from "./api/flights";
import { fetchHotels } from "./api/hotels";
import { fetchWeather } from "./api/weather";

function App() {
  const [trip, setTrip] = useState({
    destination: "",
    start_date: "",
    end_date: "",
    preferences: {}
  });
  const [itinerary, setItinerary] = useState(null);
  const [flights, setFlights] = useState([]);
  const [hotels, setHotels] = useState([]);
  const [weather, setWeather] = useState({});
  const [loading, setLoading] = useState(false);

  const handlePlan = async () => {
    setLoading(true);
    try {
      const [itin, w, f, h] = await Promise.all([
        getItinerary(trip),
        fetchWeather(trip),
        fetchFlights(trip),
        fetchHotels(trip),
      ]);
      setItinerary(itin);
      setWeather(w);
      setFlights(f);
      setHotels(h);
    } catch (e) {
      alert("Error: " + e.message);
    }
    setLoading(false);
  };

  return (
    <div style={{ display: "flex" }}>
      <Sidebar trip={trip} setTrip={setTrip} onPlan={handlePlan} loading={loading} />
      <main style={{ flex: 1, padding: "2rem" }}>
        {itinerary && (
          <section>
            <h2>AI Trip Itinerary</h2>
            <pre style={{ background: "#181d", padding: "1em" }}>
              {JSON.stringify(itinerary, null, 2)}
            </pre>
          </section>
        )}
        <WeatherSection data={weather} />
        <FlightsSection data={flights} />
        <HotelsSection data={hotels} />
      </main>
    </div>
  );
}

export default App;
