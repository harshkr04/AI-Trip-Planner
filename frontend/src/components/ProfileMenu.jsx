// frontend/src/components/ProfileMenu.jsx
import React, { useState, useEffect, useRef } from "react";
import AuthModal from "./AuthModal";
import { useTheme } from "../contexts/ThemeContext";

/**
 * ProfileMenu — clean profile dropdown.
 * - Shows Sign in / Sign up modal when not logged in
 * - Shows only Log out button when logged in
 * - Stores auth state in localStorage.ai_user (demo)
 */

export default function ProfileMenu() {
  const [open, setOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const { darkMode, toggleDarkMode } = useTheme();
  const ref = useRef();

  useEffect(() => {
    try {
      const raw = localStorage.getItem("ai_user");
      if (raw) setUser(JSON.parse(raw));
    } catch {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const openAuth = () => {
    setShowAuth(true);
    setOpen(false);
  };

  const handleAuthClose = (newUser) => {
    setShowAuth(false);
    if (newUser) {
      localStorage.setItem("ai_user", JSON.stringify(newUser));
      setUser(newUser);
    }
  };

  const signOut = () => {
    localStorage.removeItem("ai_user");
    localStorage.removeItem("ai_token");
    console.log("[AUTH] Signed out - cleared ai_user and ai_token");
    setUser(null);
    setOpen(false);
    alert("Signed out");
  };

  const handleGmailLogin = () => {
    // Demo Gmail login - in production, use OAuth
    const demoGmailUser = {
      name: "Gmail User",
      email: "user@gmail.com",
      provider: "gmail"
    };
    localStorage.setItem("ai_user", JSON.stringify(demoGmailUser));
    setUser(demoGmailUser);
    setShowAuth(false);
    setOpen(false);
    alert("Signed in with Gmail (demo)");
  };

  return (
    <div className="profile-menu" ref={ref} style={{ position: "relative" }}>
      <button
        onClick={() => (user ? setOpen((v) => !v) : openAuth())}
        style={{
          width: "100%",
          display: "flex",
          alignItems: "center",
          gap: 10,
          background: "#fff",
          border: "1px solid #e5e7eb",
          borderRadius: 10,
          padding: "10px 12px",
          cursor: "pointer",
          transition: "0.2s",
          boxShadow: "0 2px 8px rgba(15, 30, 60, 0.08)",
        }}
      >
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: 999,
            background: "#eef2ff",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: 700,
            fontSize: 16,
            color: "#4f46e5",
          }}
        >
          {user?.name ? user.name.charAt(0).toUpperCase() : "U"}
        </div>

        <div style={{ flex: 1, textAlign: "left" }}>
          <div style={{ fontWeight: 600, fontSize: 14 }}>
            {user?.name || "Sign in"}
          </div>
          <div style={{ fontSize: 12, color: "#6b7280" }}>
            {user?.email || "View profile / login"}
          </div>
        </div>

        {user && <div style={{ color: "#9ca3af" }}>▾</div>}
      </button>

      {open && user && (
        <div
          className="pm-menu"
          style={{
            position: "absolute",
            left: 8,
            bottom: 64,
            width: 220,
            background: "#fff",
            borderRadius: 12,
            boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
            border: "1px solid #e5e7eb",
            animation: "fadeIn 0.15s ease-in-out",
            zIndex: 20,
          }}
        >
          <div style={{ padding: 16, borderBottom: "1px solid #e5e7eb" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: 8,
                  background: "#eef2ff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 700,
                  fontSize: 18,
                  color: "#4f46e5",
                }}
              >
                {user.name.charAt(0).toUpperCase()}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div
                  style={{
                    fontWeight: 600,
                    fontSize: 14,
                    color: "#111827",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {user.name}
                </div>
                <div
                  style={{
                    fontSize: 12,
                    color: "#6b7280",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}
                >
                  {user.email}
                </div>
              </div>
            </div>
          </div>

          <div style={{ padding: 8, display: "flex", flexDirection: "column", gap: 8 }}>
            <button
              onClick={toggleDarkMode}
              style={{
                width: "100%",
                padding: "10px 12px",
                borderRadius: 8,
                background: "#fff",
                border: "1px solid #e5e7eb",
                cursor: "pointer",
                fontWeight: 500,
                fontSize: 14,
                color: "#374151",
                textAlign: "left",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                transition: "background 0.2s",
              }}
              onMouseEnter={(e) => (e.target.style.background = "#f3f4f6")}
              onMouseLeave={(e) => (e.target.style.background = "#fff")}
            >
              <span>Dark Mode</span>
              <span style={{ fontSize: 18 }}>{darkMode ? "🌙" : "☀️"}</span>
            </button>
            <button
              onClick={signOut}
              style={{
                width: "100%",
                padding: "10px 12px",
                borderRadius: 8,
                background: "#fff",
                border: "1px solid #e5e7eb",
                cursor: "pointer",
                fontWeight: 500,
                fontSize: 14,
                color: "#374151",
                textAlign: "center",
                transition: "background 0.2s",
              }}
              onMouseEnter={(e) => (e.target.style.background = "#f3f4f6")}
              onMouseLeave={(e) => (e.target.style.background = "#fff")}
            >
              Log out
            </button>
          </div>
        </div>
      )}

      {showAuth && <AuthModal onClose={handleAuthClose} onGmailLogin={handleGmailLogin} />}
    </div>
  );
}
