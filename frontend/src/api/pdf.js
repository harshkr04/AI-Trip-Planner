import axios from "axios";
import { API_BASE } from "../config/api";

const API_URL = `${API_BASE}/api/pdf`;

export const downloadPdf = async (payload) => {
  try {
    const response = await axios.post(
      `${API_URL}/generate`,
      {
        title: payload.title || "Trip Itinerary",
        itinerary_text: payload.itinerary || payload.itinerary_text || "",
        itinerary_days: payload.itinerary_days || [],
        destination: payload.destination || "",
        cover_image: payload.cover_image || "",
        summary: payload.summary || "",
        overall_tips: payload.overall_tips || [],
      },
      {
        responseType: "blob",
        headers: {
          "Content-Type": "application/json",
        },
      }
    );

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "trip-itinerary.pdf");
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    return true;
  } catch (error) {
    console.error("PDF download error:", error.response?.data || error.message);
    throw error;
  }
};

export const sharePdfByEmail = async ({ email, subject, message, itineraryPayload }) => {
  const response = await axios.post(`${API_URL}/email`, {
    email,
    subject,
    message,
    title: itineraryPayload.title || "Your AI Travel Plan",
    itinerary_text: itineraryPayload.itinerary || itineraryPayload.itinerary_text || "",
    itinerary_days: itineraryPayload.itinerary_days || [],
    destination: itineraryPayload.destination || "",
    cover_image: itineraryPayload.cover_image || "",
    summary: itineraryPayload.summary || "",
    overall_tips: itineraryPayload.overall_tips || [],
  });
  return response.data;
};
