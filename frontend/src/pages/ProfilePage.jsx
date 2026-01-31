// frontend/src/pages/ProfilePage.jsx
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function ProfilePage() {
    const [user, setUser] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        const storedUser = localStorage.getItem("ai_user");
        if (storedUser) {
            setUser(JSON.parse(storedUser));
        } else {
            navigate("/");
        }
    }, [navigate]);

    const handleLogout = () => {
        localStorage.removeItem("ai_user");
        localStorage.removeItem("ai_token");
        navigate("/");
        window.location.reload(); // Force reload to clear state
    };

    if (!user) return null;

    return (
        <div className="page-container" style={{ padding: "40px 20px", maxWidth: "800px", margin: "0 auto" }}>
            <div className="card" style={{ padding: "32px", textAlign: "center" }}>
                <div style={{ marginBottom: "24px" }}>
                    {user.picture ? (
                        <img
                            src={user.picture}
                            alt={user.name}
                            style={{
                                width: "120px",
                                height: "120px",
                                borderRadius: "50%",
                                objectFit: "cover",
                                border: "4px solid white",
                                boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                            }}
                        />
                    ) : (
                        <div
                            style={{
                                width: "120px",
                                height: "120px",
                                borderRadius: "50%",
                                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                                color: "white",
                                fontSize: "48px",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                                margin: "0 auto",
                                fontWeight: "bold",
                            }}
                        >
                            {user.name ? user.name.charAt(0).toUpperCase() : "U"}
                        </div>
                    )}
                </div>

                <h1 style={{ fontSize: "28px", marginBottom: "8px", color: "#2d3748" }}>{user.name}</h1>
                <p style={{ fontSize: "16px", color: "#718096", marginBottom: "32px" }}>{user.email}</p>

                <div style={{ display: "grid", gap: "16px", maxWidth: "400px", margin: "0 auto" }}>
                    <div className="stat-card" style={{ padding: "16px", background: "#f7fafc", borderRadius: "12px" }}>
                        <div style={{ fontSize: "24px", fontWeight: "bold", color: "#4a5568" }}>0</div>
                        <div style={{ fontSize: "14px", color: "#718096" }}>Saved Itineraries</div>
                    </div>
                </div>

                <button
                    onClick={handleLogout}
                    style={{
                        marginTop: "40px",
                        padding: "12px 32px",
                        background: "#fff",
                        border: "1px solid #e2e8f0",
                        borderRadius: "8px",
                        color: "#e53e3e",
                        fontWeight: "600",
                        cursor: "pointer",
                        transition: "all 0.2s",
                    }}
                    onMouseEnter={(e) => (e.target.style.background = "#fff5f5")}
                    onMouseLeave={(e) => (e.target.style.background = "#fff")}
                >
                    Sign Out
                </button>
            </div>
        </div>
    );
}
