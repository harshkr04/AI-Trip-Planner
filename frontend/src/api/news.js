import axios from "axios";
const API = "http://localhost:8000";

export async function fetchNews(q = "travel") {
  // backend route: GET /api/news?q=travel
  const res = await axios.get(`${API}/api/news`, { params: { q } });
  return res.data;
}
