// frontend/src/App.js
import React, { useState, useEffect } from "react";
import { Routes, Route, useNavigate, Navigate, useLocation } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import HomePage from "./pages/HomePage";
import FlightSearch from "./pages/FlightSearch";
import HotelSearch from "./pages/HotelSearch";
import NewsPage from "./pages/NewsPage";
import "./App.css";

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  useEffect(() => {
    try {
      const raw = localStorage.getItem("ai_chat_sessions");
      if (raw) setSessions(JSON.parse(raw));
    } catch (e) {
      setSessions([]);
    }
  }, []);

  const saveSessions = (newSessions) => {
    setSessions(newSessions);
    localStorage.setItem("ai_chat_sessions", JSON.stringify(newSessions));
    // save latest to server (non-blocking)
    const API_BASE = process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '';
    fetch(`${API_BASE}/api/sessions/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newSessions[0]),
    }).catch(() => {});
  };

  function handleLoadSession(s) {
    setSelectedSession(s);
    navigate("/");
  }

  function handleNewChat() {
    setSelectedSession(null);
    navigate("/");
    setMobileSidebarOpen(false);
  }

  const homeElement = (
    <HomePage sessions={sessions} saveSessions={saveSessions} selectedSession={selectedSession} />
  );

  useEffect(() => {
    if (!isMobileSidebarOpen) return;
    const handleKey = (event) => {
      if (event.key === "Escape") setMobileSidebarOpen(false);
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [isMobileSidebarOpen]);

  useEffect(() => {
    if (isMobileSidebarOpen) setMobileSidebarOpen(false);
  }, [location.pathname, isMobileSidebarOpen]);

  useEffect(() => {
    if (typeof document === "undefined") return;
    document.body.classList.toggle("sidebar-mobile-open", isMobileSidebarOpen);
    return () => {
      document.body.classList.remove("sidebar-mobile-open");
    };
  }, [isMobileSidebarOpen]);

  return (
    <div className="app">
      <Sidebar
        sessions={sessions}
        onLoadSession={handleLoadSession}
        onNewChat={handleNewChat}
        isMobileOpen={isMobileSidebarOpen}
        onCloseMobile={() => setMobileSidebarOpen(false)}
      />
      {isMobileSidebarOpen && <div className="sidebar-overlay" onClick={() => setMobileSidebarOpen(false)} />}
      <main className="stage">
        <button className="mobile-menu-toggle" type="button" onClick={() => setMobileSidebarOpen(true)} aria-label="Open navigation">
          ☰
        </button>
        <div className="stage-inner">
          <Routes>
            <Route path="/" element={homeElement} />
            <Route path="/flights" element={<FlightSearch />} />
            <Route path="/hotels" element={<HotelSearch />} />
            <Route path="/news" element={<NewsPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}
