// frontend/src/App.js
import React, { useState, useEffect } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
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
    fetch("/api/sessions/save", {
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
  }

  return (
    <div className="app">
      <Sidebar sessions={sessions} onLoadSession={handleLoadSession} onNewChat={handleNewChat} />
      <main className="stage">
        <Routes>
          <Route path="/" element={<HomePage sessions={sessions} saveSessions={saveSessions} selectedSession={selectedSession} />} />
          <Route path="/flights" element={<FlightSearch />} />
          <Route path="/hotels" element={<HotelSearch />} />
          <Route path="/news" element={<NewsPage />} />
        </Routes>
      </main>
    </div>
  );
}
