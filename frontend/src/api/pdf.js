import axios from 'axios';

const API_URL = 'http://localhost:8000/api/pdf';

export const downloadPdf = async (data) => {
  try {
    // Send POST request with itinerary data
    const response = await axios.post(`${API_URL}/generate`, {
      title: data.title || "Trip Itinerary",
      itinerary: data.itinerary || ""
    }, {
      responseType: 'blob',  // Important for PDF download
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    // Create download link
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'trip-itinerary.pdf');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    return true;
  } catch (error) {
    console.error('PDF download error:', error.response?.data || error.message);
    throw error;
  }
};
