import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { ThemeProvider } from "./contexts/ThemeContext";
import App from "./App";
import "./index.css";
import "./App.css";

// Get basename from package.json homepage or default
const getBasename = () => {
  if (process.env.PUBLIC_URL) return process.env.PUBLIC_URL;
  // Check if we're on GitHub Pages
  if (window.location.pathname.includes('/AI-Trip-Planner')) {
    return '/AI-Trip-Planner';
  }
  return '';
};

const root = createRoot(document.getElementById("root"));
root.render(
  <BrowserRouter basename={getBasename()}>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </BrowserRouter>
);