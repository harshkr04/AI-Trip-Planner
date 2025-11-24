// frontend/src/components/AuthModal.jsx
import React, { useState, useEffect } from "react";
import "./AuthModal.css";

const EyeIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
    <circle cx="12" cy="12" r="3"></circle>
  </svg>
);

const EyeOffIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
    <line x1="1" y1="1" x2="23" y2="23"></line>
  </svg>
);

export default function AuthModal({ onClose }) {
  const [mode, setMode] = useState("signup"); // Default to signup as per request
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Reset error when switching modes
  useEffect(() => {
    setError("");
    setEmail("");
    setName("");
    setPassword("");
    setConfirmPassword("");
  }, [mode]);

  const close = (user) => {
    onClose && onClose(user || null);
  };

  const validateEmail = (email) => {
    return /\S+@\S+\.\S+/.test(email);
  };

  const submit = async () => {
    setError("");

    // Validation
    if (!email.trim() || !password) {
      setError("Please provide all required fields.");
      return;
    }
    if (!validateEmail(email)) {
      setError("Please enter a valid email address.");
      return;
    }
    if (mode === "signup") {
      if (!name.trim()) {
        setError("Please enter your full name.");
        return;
      }
      if (password.length < 6) {
        setError("Password must be at least 6 characters.");
        return;
      }
      if (password !== confirmPassword) {
        setError("Passwords do not match.");
        return;
      }
    }

    setLoading(true);
    try {
      // Determine API base URL - prioritize environment variable or default to localhost
      const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const endpoint = mode === "signup" ? "/api/auth/register" : "/api/auth/login";

      const payload = mode === "signup"
        ? { email, password, name }
        : { email, password };

      console.log(`Attempting ${mode} at ${API_BASE}${endpoint}`);
      console.log("Payload:", JSON.stringify(payload, null, 2)); // Debug logging

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      let data;
      try {
        data = await res.json();
      } catch (jsonError) {
        console.error("JSON Parse Error:", jsonError);
        throw new Error("Server returned an invalid response (not JSON). Check API URL.");
      }

      if (!res.ok) {
        console.error("Auth Error Response:", res.status, data);

        if (res.status === 409) {
          throw new Error("Email already registered. Please sign in.");
        }

        if (res.status === 401) {
          throw new Error(data.detail || "Invalid email or password.");
        }

        if (res.status === 404) {
          throw new Error("Authentication service not found. Please contact support.");
        }

        if (res.status === 422 && data.detail) {
          if (Array.isArray(data.detail)) {
            const errorMsg = data.detail.map(err => `${err.loc[1] || 'Field'}: ${err.msg}`).join(', ');
            throw new Error(errorMsg);
          }
          throw new Error(typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail));
        }

        throw new Error(data.detail || `Authentication failed (${res.status})`);
      }

      // Success - handle both 200 and 201
      if (res.status === 201 || res.status === 200) {
        console.log("Auth Success:", data);
        localStorage.setItem("ai_user", JSON.stringify(data.user));
        if (data.token) {
          localStorage.setItem("ai_token", data.token);
        }

        close(data.user);
      }
    } catch (err) {
      console.error("Auth Exception:", err);
      setError(err.message || "Failed to connect to server. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // Handle Enter key
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      submit();
    }
  };

  return (
    <div className="auth-overlay" onClick={() => close(null)}>
      <div className="auth-card" onClick={e => e.stopPropagation()}>
        <div className="auth-head">
          <h2 className="auth-title">{mode === "signup" ? "Create account" : "Sign in"}</h2>
          <button className="auth-close" onClick={() => close(null)} aria-label="Close">
            ✕
          </button>
        </div>

        {error && <div className="auth-error-banner">{error}</div>}

        {mode === "signup" && (
          <div className="auth-field">
            <label>Full name</label>
            <div className="auth-input-wrapper">
              <input
                className="auth-input"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. John Doe"
                disabled={loading}
                onKeyDown={handleKeyDown}
              />
            </div>
          </div>
        )}

        <div className="auth-field">
          <label>Email</label>
          <div className="auth-input-wrapper">
            <input
              className="auth-input"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@example.com"
              disabled={loading}
              onKeyDown={handleKeyDown}
            />
          </div>
        </div>

        <div className="auth-field">
          <label>Password</label>
          <div className="auth-input-wrapper">
            <input
              className="auth-input"
              type={showPassword ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              disabled={loading}
              onKeyDown={handleKeyDown}
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword(!showPassword)}
              tabIndex="-1"
            >
              {showPassword ? <EyeOffIcon /> : <EyeIcon />}
            </button>
          </div>
        </div>

        {mode === "signup" && (
          <div className="auth-field">
            <label>Confirm Password</label>
            <div className="auth-input-wrapper">
              <input
                className="auth-input"
                type={showConfirmPassword ? "text" : "password"}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                disabled={loading}
                onKeyDown={handleKeyDown}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                tabIndex="-1"
              >
                {showConfirmPassword ? <EyeOffIcon /> : <EyeIcon />}
              </button>
            </div>
          </div>
        )}

        <div className="auth-actions">
          <button className="auth-primary" onClick={submit} disabled={loading}>
            {loading ? (
              <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <svg className="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                  <circle cx="12" cy="12" r="10" strokeOpacity="0.25"></circle>
                  <path d="M12 2a10 10 0 0 1 10 10" strokeOpacity="1"></path>
                </svg>
                Processing...
              </span>
            ) : (
              mode === "signup" ? "Create account" : "Sign in"
            )}
          </button>

          <button
            className="auth-secondary"
            onClick={() => {
              setMode(mode === "signup" ? "login" : "signup");
              setError("");
            }}
            disabled={loading}
          >
            {mode === "signup" ? "Have an account? Sign in" : "Create account"}
          </button>
        </div>
      </div>
      <style>{`
        .animate-spin {
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
