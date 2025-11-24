// frontend/src/components/HotelCard.jsx
import React from "react";

export default function HotelCard({ hotel }) {
    const isRealTime = hotel.source !== "mock";

    return (
        <div className="hotel-card" style={{
            background: "var(--surface-card)",
            border: "1px solid var(--border-subtle)",
            borderRadius: "12px",
            padding: "16px",
            marginBottom: "12px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
            transition: "transform 0.2s ease, box-shadow 0.2s ease"
        }}>
            <div style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                    <h4 style={{ margin: 0, fontSize: "1.1rem" }}>{hotel.name}</h4>
                    {isRealTime && (
                        <span style={{
                            fontSize: "0.75rem",
                            color: "#10b981",
                            background: "#ecfdf5",
                            padding: "2px 6px",
                            borderRadius: "4px",
                            border: "1px solid #a7f3d0"
                        }}>
                            Live Rate
                        </span>
                    )}
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "0.9rem", color: "var(--text-muted)" }}>
                    <span>{hotel.area || "City Center"}</span>
                    <span>•</span>
                    <span style={{ color: "#f59e0b", fontWeight: "bold" }}>{hotel.rating} ★</span>
                </div>
            </div>

            <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: "1.25rem", fontWeight: "bold", color: "var(--text-main)" }}>
                    ₹{hotel.price_per_night.toLocaleString()}
                    <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: "normal" }}>/night</span>
                </div>
                <button className="btn-secondary" style={{ marginTop: "8px", padding: "6px 12px", fontSize: "0.9rem" }}>
                    View Deal
                </button>
            </div>
        </div>
    );
}
