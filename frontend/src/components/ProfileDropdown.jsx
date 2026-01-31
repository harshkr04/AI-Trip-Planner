// frontend/src/components/ProfileDropdown.jsx
import React, { useEffect, useRef } from "react";
import "./ProfileDropdown.css";

export default function ProfileDropdown({ user, onProfileClick, onLogoutClick, onClose }) {
    const dropdownRef = useRef(null);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                onClose();
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [onClose]);

    return (
        <div className="profile-dropdown" ref={dropdownRef}>
            <div className="profile-dropdown-header">
                <div className="profile-dropdown-avatar">
                    {user?.name ? user.name.charAt(0).toUpperCase() : "U"}
                </div>
                <div className="profile-dropdown-info">
                    <div className="profile-dropdown-name">{user?.name || "User"}</div>
                    <div className="profile-dropdown-email">{user?.email || ""}</div>
                </div>
            </div>

            <div className="profile-dropdown-divider"></div>

            <div className="profile-dropdown-menu">
                <button
                    className="profile-dropdown-item"
                    onClick={() => {
                        onProfileClick();
                        onClose();
                    }}
                >
                    <span className="profile-dropdown-icon">👤</span>
                    Profile
                </button>

                <button
                    className="profile-dropdown-item profile-dropdown-item-danger"
                    onClick={() => {
                        onLogoutClick();
                        onClose();
                    }}
                >
                    <span className="profile-dropdown-icon">🚪</span>
                    Logout
                </button>
            </div>
        </div>
    );
}
