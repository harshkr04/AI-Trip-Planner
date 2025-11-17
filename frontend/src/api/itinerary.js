// frontend/src/api/itinerary.js
import axios from "axios";

const API = "http://localhost:8000";

export async function createItinerary({ prompt, start_date, end_date }) {
  const res = await axios.post(`${API}/api/itinerary/generate`, { prompt, start_date, end_date });
  return res.data; // { itinerary_text, weather, flights, hotels }
}
