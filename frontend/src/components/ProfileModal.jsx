// frontend/src/components/ProfileModal.jsx
import React, { useState, useRef } from "react";
import { createPortal } from "react-dom";
import "./ProfileModal.css";

export default function ProfileModal({ user, onClose, onSave, onImageChange }) {
    const [displayName, setDisplayName] = useState(user?.name || "");
    const [username, setUsername] = useState(user?.email?.split("@")[0] || "");
    const [profileImage, setProfileImage] = useState(user?.picture || null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const fileInputRef = useRef(null);

    const getInitials = () => {
        if (!displayName) return "U";
        const parts = displayName.trim().split(" ");
        if (parts.length >= 2) {
            return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
        }
        return displayName.charAt(0).toUpperCase();
    };

    const handleImageUpload = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (file.size > 5 * 1024 * 1024) {
                setError("Image size must be less than 5MB");
                return;
            }

            const reader = new FileReader();
            reader.onloadend = () => {
                setProfileImage(reader.result);
                if (onImageChange) {
                    onImageChange(reader.result);
                }
                setError("");
            };
            reader.readAsDataURL(file);
        }
    };

    const handleSave = async () => {
        setError("");

        if (!displayName.trim()) {
            setError("Display name is required");
            return;
        }

        if (!username.trim()) {
            setError("Username is required");
            return;
        }

        setLoading(true);
        try {
            const API_BASE = process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '';

            const response = await fetch(`${API_BASE}/api/auth/update-profile`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${localStorage.getItem("ai_token")}`
                },
                body: JSON.stringify({
                    id: user.id,
                    name: displayName.trim(),
                    email: username.includes("@") ? username : `${username}@example.com`,
                    picture: profileImage
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "Failed to update profile");
            }

            // Update localStorage
            localStorage.setItem("ai_user", JSON.stringify(data.user));

            if (onSave) {
                onSave(data.user);
            }

            onClose();
        } catch (err) {
            console.error("Profile update error:", err);
            setError(err.message || "Failed to update profile");
        } finally {
            setLoading(false);
        }
    };

    return createPortal(
        <div className="profile-modal-overlay" onClick={onClose}>
            <div className="profile-modal" onClick={(e) => e.stopPropagation()}>
                <div className="profile-modal-header">
                    <h2 className="profile-modal-title">Edit profile</h2>
                    <button
                        className="profile-modal-close"
                        onClick={onClose}
                        aria-label="Close modal"
                    >
                        ✕
                    </button>
                </div>

                <div className="profile-modal-content">
                    {error && (
                        <div className="profile-modal-error">{error}</div>
                    )}

                    <div className="profile-modal-avatar-section">
                        <div className="profile-modal-avatar-wrapper">
                            {profileImage ? (
                                <img
                                    src={profileImage}
                                    alt="Profile"
                                    className="profile-modal-avatar-image"
                                />
                            ) : (
                                <div className="profile-modal-avatar">
                                    {getInitials()}
                                </div>
                            )}
                            <button
                                className="profile-modal-avatar-upload"
                                onClick={() => fileInputRef.current?.click()}
                                aria-label="Upload profile picture"
                            >
                                📷
                            </button>
                        </div>
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/*"
                            onChange={handleImageUpload}
                            style={{ display: "none" }}
                        />
                    </div>

                    <div className="profile-modal-field">
                        <label className="profile-modal-label">Display name</label>
                        <input
                            type="text"
                            className="profile-modal-input"
                            value={displayName}
                            onChange={(e) => setDisplayName(e.target.value)}
                            placeholder="Enter your display name"
                            disabled={loading}
                        />
                    </div>

                    <div className="profile-modal-field">
                        <label className="profile-modal-label">Username</label>
                        <input
                            type="text"
                            className="profile-modal-input"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Enter your username"
                            disabled={loading}
                        />
                    </div>
                </div>

                <div className="profile-modal-footer">
                    <button
                        className="profile-modal-button profile-modal-button-secondary"
                        onClick={onClose}
                        disabled={loading}
                    >
                        Cancel
                    </button>
                    <button
                        className="profile-modal-button profile-modal-button-primary"
                        onClick={handleSave}
                        disabled={loading}
                    >
                        {loading ? "Saving..." : "Save"}
                    </button>
                </div>
            </div>
        </div>,
        document.body
    );
}
