import axios from "axios";
const API = "http://localhost:8000";

export async function searchFlights(payload) {
  // backend route expects POST /api/flights with payload { origin, destination, start_date }
  const res = await axios.post(`${API}/api/flights`, payload);
  return res.data;
}
