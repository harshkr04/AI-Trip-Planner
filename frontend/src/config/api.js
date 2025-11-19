// frontend/src/config/api.js
// Centralized API configuration that handles both dev and production

const getApiBase = () => {
  // In development, use localhost
  if (process.env.NODE_ENV === 'development') {
    return 'http://localhost:8000';
  }
  // In production, use relative paths (works with subpath deployment)
  return '';
};

export const API_BASE = getApiBase();

// Helper function for API calls
export const apiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE}${endpoint}`;
  return fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
};

