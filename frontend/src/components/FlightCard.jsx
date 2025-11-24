// frontend/src/components/FlightCard.jsx
import React from "react";

export default function FlightCard({ flight }) {
    const isRealTime = flight.source !== "mock";

    return (
        <div className="flight-card" style={{
            background: "var(--surface-card)",
            border: "1px solid var(--border-subtle)",
            borderRadius: "12px",
            padding: "16px",
            marginBottom: "12px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
            transition: "transform 0.2s ease, box-shadow 0.2s ease",
            cursor: "pointer"
        }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <span className="chip" style={{
                        background: "var(--primary-light)",
                        color: "var(--primary)",
                        fontWeight: 600,
                        fontSize: "0.85rem"
                    }}>
                        {flight.airline}
                    </span>
                    {isRealTime && (
                        <span style={{
                            fontSize: "0.75rem",
                            color: "#10b981",
                            background: "#ecfdf5",
                            padding: "2px 6px",
                            borderRadius: "4px",
                            border: "1px solid #a7f3d0"
                        }}>
                            Real-time
                        </span>
                    )}
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "12px", marginTop: "8px" }}>
                    <div style={{ textAlign: "center" }}>
                        <div style={{ fontSize: "1.1rem", fontWeight: "bold" }}>{flight.from}</div>
                    </div>
                    <div style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>→</div>
                    <div style={{ textAlign: "center" }}>
                        <div style={{ fontSize: "1.1rem", fontWeight: "bold" }}>{flight.to}</div>
                    </div>
                </div>
                <div style={{ fontSize: "0.9rem", color: "var(--text-muted)" }}>
                    Depart: {new Date(flight.depart).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}
                </div>
            </div>

            <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: "1.25rem", fontWeight: "bold", color: "var(--text-main)" }}>
                    ₹{flight.price.toLocaleString()}
                </div>
                <button className="btn-primary" style={{ marginTop: "8px", padding: "6px 12px", fontSize: "0.9rem" }}>
                    Book
                </button>
            </div>
        </div>
    );
}
