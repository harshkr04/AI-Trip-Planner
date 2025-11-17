// frontend/src/components/AuthModal.jsx
import React, { useState } from "react";

/**
 * AuthModal (v2)
 * Larger, centered modal for Sign in / Sign up.
 * Still uses demo localStorage auth for now.
 */

export default function AuthModal({ onClose }) {
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
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(15,23,42,0.6)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 9999,
        backdropFilter: "blur(2px)",
      }}
    >
      <div
        style={{
          width: "480px", // Increased width
          background: "#fff",
          borderRadius: "16px",
          padding: "32px 28px",
          boxShadow: "0 20px 40px rgba(0,0,0,0.15)",
          animation: "fadeIn 0.2s ease",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 20,
          }}
        >
          <h2 style={{ margin: 0, fontWeight: 700, fontSize: "20px" }}>
            {mode === "signup" ? "Create account" : "Sign in"}
          </h2>
          <button
            onClick={() => close(null)}
            style={{
              border: "none",
              background: "transparent",
              fontSize: "18px",
              cursor: "pointer",
              color: "#475569",
            }}
            title="Close"
          >
            ✕
          </button>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {mode === "signup" && (
            <div>
              <label
                style={{
                  display: "block",
                  fontSize: 13,
                  color: "#475569",
                  marginBottom: 4,
                }}
              >
                Full name
              </label>
              <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your name"
                style={{
                  width: "100%",
                  padding: "10px 12px",
                  borderRadius: 10,
                  border: "1px solid #e2e8f0",
                  fontSize: 14,
                }}
              />
            </div>
          )}

          <div>
            <label
              style={{
                display: "block",
                fontSize: 13,
                color: "#475569",
                marginBottom: 4,
              }}
            >
              Email
            </label>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              style={{
                width: "100%",
                padding: "10px 12px",
                borderRadius: 10,
                border: "1px solid #e2e8f0",
                fontSize: 14,
              }}
            />
          </div>

          <div>
            <label
              style={{
                display: "block",
                fontSize: 13,
                color: "#475569",
                marginBottom: 4,
              }}
            >
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="password"
              style={{
                width: "100%",
                padding: "10px 12px",
                borderRadius: 10,
                border: "1px solid #e2e8f0",
                fontSize: 14,
              }}
            />
          </div>
        </div>

        <div
          style={{
            display: "flex",
            gap: 10,
            marginTop: 24,
          }}
        >
          <button
            onClick={submit}
            style={{
              flex: 1,
              padding: "12px 16px",
              borderRadius: 10,
              background: "linear-gradient(90deg,#6b46c1,#7c3aed)",
              color: "white",
              fontWeight: 600,
              fontSize: 15,
              border: "none",
              cursor: "pointer",
            }}
          >
            {mode === "signup" ? "Create account" : "Sign in"}
          </button>
          <button
            onClick={() => setMode(mode === "signup" ? "login" : "signup")}
            style={{
              padding: "12px 16px",
              borderRadius: 10,
              background: "#f1f5f9",
              border: "1px solid #e6eef8",
              cursor: "pointer",
              fontWeight: 500,
            }}
          >
            {mode === "signup" ? "Have an account?" : "Create account"}
          </button>
        </div>
      </div>
    </div>
  );
}
