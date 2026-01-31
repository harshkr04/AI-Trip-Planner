// frontend/src/App.js
import React, { useState, useEffect } from "react";
import { Routes, Route, useNavigate, Navigate, useLocation } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import AuthModal from "./components/AuthModal";
import HomePage from "./pages/HomePage";
import FlightSearch from "./pages/FlightSearch";
import HotelSearch from "./pages/HotelSearch";
import NewsPage from "./pages/NewsPage";
import "./App.css";
// Trigger reload

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    try {
      const raw = localStorage.getItem("ai_chat_sessions");
      if (raw) setSessions(JSON.parse(raw));

      const rawUser = localStorage.getItem("ai_user");
      if (rawUser) setUser(JSON.parse(rawUser));

      const savedTheme = localStorage.getItem("ai_theme");
      if (savedTheme === "dark") setIsDarkMode(true);
    } catch (e) {
      console.error("Failed to load local storage data", e);
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
    }).catch(() => { });
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

  const handleSignInClick = () => {
    setShowAuthModal(true);
  };

  const handleAuthClose = (loggedInUser) => {
    setShowAuthModal(false);
    if (loggedInUser) {
      setUser(loggedInUser);
    }
  };

  const handleUserUpdate = (updatedUser) => {
    setUser(updatedUser);
    if (updatedUser) {
      localStorage.setItem("ai_user", JSON.stringify(updatedUser));
    } else {
      localStorage.removeItem("ai_user");
      localStorage.removeItem("ai_token");
    }
  };

  const toggleTheme = () => {
    setIsDarkMode((prev) => {
      const newMode = !prev;
      localStorage.setItem("ai_theme", newMode ? "dark" : "light");
      return newMode;
    });
  };

  const homeElement = (
    <HomePage
      sessions={sessions}
      saveSessions={saveSessions}
      selectedSession={selectedSession}
      isDarkMode={isDarkMode}
      toggleTheme={toggleTheme}
    />
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
    <div className="app" data-theme={isDarkMode ? "dark" : "light"}>
      <Sidebar
        sessions={sessions}
        onLoadSession={handleLoadSession}
        onNewChat={handleNewChat}
        isMobileOpen={isMobileSidebarOpen}
        onCloseMobile={() => setMobileSidebarOpen(false)}
        onSignInClick={handleSignInClick}
        onUserUpdate={handleUserUpdate}
        user={user}
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
      {showAuthModal && <AuthModal onClose={handleAuthClose} />}
      <div style={{ position: 'fixed', bottom: 0, right: 0, padding: '4px', fontSize: '10px', opacity: 0.5, pointerEvents: 'none' }}>v2.0</div>
    </div>
  );
}
