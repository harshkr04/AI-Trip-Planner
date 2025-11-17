import axios from "axios";
const API = "http://localhost:8000";

export async function searchHotels(payload) {
  // backend route expects POST /api/hotels with { destination, start_date, end_date }
  const res = await axios.post(`${API}/api/hotels`, payload);
  return res.data;
}
