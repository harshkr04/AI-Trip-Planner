// frontend/src/components/AuthModal.jsx
import React, { useState } from "react";

/**
 * AuthModal (v2)
 * Larger, centered modal for Sign in / Sign up.
 * Still uses demo localStorage auth for now.
 */
export default function AuthModal({ onClose, onGmailLogin }) {
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");

  const close = (user) => {
    onClose && onClose(user || null);
  };

  const submit = () => {
    if (!email || !password) {
      alert("Please provide email and password.");
      return;
    }
    if (mode === "signup" && !name) {
      alert("Please enter your name to sign up.");
      return;
    }

    const user = { name: name || email.split("@")[0], email };
    localStorage.setItem("ai_user", JSON.stringify(user));
    alert(mode === "signup" ? "Account created (demo)" : "Signed in (demo)");
    close(user);
  };

  return (
    <div className="auth-overlay">
      <div className="auth-card">
        <div className="auth-head">
          <h2 className="auth-title">{mode === "signup" ? "Create account" : "Sign in"}</h2>
          <button className="auth-close" onClick={() => close(null)} aria-label="Close auth modal">
            ✕
          </button>
        </div>

        {mode === "signup" && (
          <div className="auth-field">
            <label>Full name</label>
            <input
              className="auth-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your name"
            />
          </div>
        )}

        <div className="auth-field">
          <label>Email</label>
          <input
            className="auth-input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
          />
        </div>

        <div className="auth-field">
          <label>Password</label>
          <input
            className="auth-input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="password"
          />
        </div>

        {onGmailLogin && (
          <div style={{ marginTop: 16, marginBottom: 8 }}>
            <div style={{ textAlign: "center", fontSize: 13, color: "var(--muted)", marginBottom: 12 }}>or</div>
            <button
              className="auth-gmail"
              onClick={onGmailLogin}
              style={{
                width: "100%",
                height: "48px",
                borderRadius: "14px",
                border: "1px solid rgba(23, 35, 57, 0.12)",
                background: "#fff",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "10px",
                cursor: "pointer",
                fontWeight: 600,
                fontSize: 15,
                transition: "all 0.2s ease",
              }}
              onMouseEnter={(e) => {
                e.target.style.background = "#f8f9fa";
                e.target.style.borderColor = "var(--accent)";
              }}
              onMouseLeave={(e) => {
                e.target.style.background = "#fff";
                e.target.style.borderColor = "rgba(23, 35, 57, 0.12)";
              }}
            >
              <span>📧</span>
              <span>Continue with Gmail</span>
            </button>
          </div>
        )}

        <div className="auth-actions">
          <button className="auth-primary" onClick={submit}>
            {mode === "signup" ? "Create account" : "Sign in"}
          </button>
          <button className="auth-secondary" onClick={() => setMode(mode === "signup" ? "login" : "signup")}>
            {mode === "signup" ? "Have an account?" : "Create account"}
          </button>
        </div>
      </div>
    </div>
  );
}
