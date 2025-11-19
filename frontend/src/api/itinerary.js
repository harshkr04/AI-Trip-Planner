// frontend/src/api/itinerary.js
import axios from "axios";
import { API_BASE } from "../config/api";

export async function createItinerary({ prompt, start_date, end_date, origin }) {
  const res = await axios.post(`${API_BASE}/api/itinerary/generate`, {
    prompt,
    start_date,
    end_date,
    origin,
  });
  return res.data;
}

export async function refineItinerary({ itineraryId, instruction }) {
  const res = await axios.post(`${API_BASE}/api/itinerary/refine`, {
    itinerary_id: itineraryId,
    instruction,
  });
  return res.data;
}

export async function saveDayNote({ itineraryId, day, note }) {
  const res = await axios.post(`${API_BASE}/api/itinerary/${itineraryId}/day/${day}/note`, {
    note,
  });
  return res.data;
}
