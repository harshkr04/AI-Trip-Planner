// frontend/src/components/Sidebar.jsx
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createPortal } from "react-dom";
import ProfileDropdown from "./ProfileDropdown";
import ProfileModal from "./ProfileModal";
import "./Sidebar.css";

export default function Sidebar({
    sessions,
    onLoadSession,
    onDeleteSession,
    onNewChat,
    isMobileOpen,
    onCloseMobile,
    onSignInClick,
    onUserUpdate,
    user
}) {
    const [searchQuery, setSearchQuery] = useState("");
    const [showDropdown, setShowDropdown] = useState(false);
    const [showProfileModal, setShowProfileModal] = useState(false);
    const [deleteConfirmation, setDeleteConfirmation] = useState(null);
    const navigate = useNavigate();

    const [previewImage, setPreviewImage] = useState(null);

    const navItems = [
        { path: "/flights", label: "Flight Search", icon: "✈️" },
        { path: "/hotels", label: "Hotels & Cuisines", icon: "🏨" },
        { path: "/news", label: "Travel News & Blogs", icon: "📰" }
    ];

    const filteredSessions = sessions.filter(s =>
        s.title?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.prompt?.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const handleDeleteClick = (e, sessionId) => {
        e.stopPropagation();
        setDeleteConfirmation(sessionId);
    };

    const confirmDelete = () => {
        if (deleteConfirmation && onDeleteSession) {
            onDeleteSession(deleteConfirmation);
        }
        setDeleteConfirmation(null);
    };

    const cancelDelete = () => {
        setDeleteConfirmation(null);
    };

    const handleProfileClick = () => {
        setShowProfileModal(true);
    };

    const handleLogout = () => {
        // Clear all auth state
        localStorage.removeItem("ai_user");
        localStorage.removeItem("ai_token");
        console.log("[AUTH] Logged out - cleared ai_user and ai_token");

        // Notify parent component to clear state
        if (onUserUpdate) {
            onUserUpdate(null);
        }

        // Navigate to home
        navigate("/AI-Trip-Planner");
    };

    const handleProfileSave = (updatedUser) => {
        if (onUserUpdate) {
            onUserUpdate(updatedUser);
        }
        setPreviewImage(null); // Clear preview as user data is updated
    };

    const handleProfileClose = () => {
        setShowProfileModal(false);
        setPreviewImage(null); // Clear preview on cancel/close
    };

    const handleImageChange = (newImage) => {
        setPreviewImage(newImage);
    };

    return (
        <aside className={`sidebar-root ${isMobileOpen ? "sidebar-mobile-open" : ""}`}>
            <button className="btn-new" onClick={onNewChat}>
                + NEW CHAT
            </button>

            <div className="search-container">
                <input
                    type="text"
                    className="search-input"
                    placeholder="Search chats"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
            </div>

            <div className="sidebar-card chat-history-card">
                <div className="sidebar-card-header">CHAT HISTORY</div>
                <div className="history-list">
                    {filteredSessions.length > 0 ? (
                        filteredSessions.slice(0, 10).map((s) => (
                            <div
                                key={s.id}
                                className="chat-pill"
                                onClick={() => {
                                    onLoadSession(s);
                                    onCloseMobile();
                                }}
                            >
                                <div className="chat-pill-content">
                                    <span className="chat-pill-title">
                                        {s.title || s.prompt?.substring(0, 20) || "New Chat"}...
                                    </span>
                                    <span className="chat-pill-view">View</span>
                                </div>
                                <button
                                    className="chat-pill-delete"
                                    onClick={(e) => handleDeleteClick(e, s.id)}
                                    title="Delete"
                                >
                                    🗑️
                                </button>
                            </div>
                        ))
                    ) : (
                        <div className="empty-history">No chats found</div>
                    )}
                </div>
            </div>

            <div className="sidebar-card nav-card">
                <div className="sidebar-card-header">NAVIGATION</div>
                <div className="nav-list">
                    {navItems.map((item) => (
                        <Link
                            key={item.path}
                            to={item.path}
                            className="nav-pill"
                            onClick={onCloseMobile}
                        >
                            <span className="nav-icon">{item.icon}</span>
                            <span className="nav-label">{item.label}</span>
                        </Link>
                    ))}
                </div>
            </div>

            <div className="sidebar-footer">
                <button
                    className="sign-in-button"
                    onClick={() => {
                        if (user) {
                            setShowDropdown(!showDropdown);
                        } else {
                            onSignInClick && onSignInClick();
                        }
                    }}
                >
                    {user ? (
                        <>
                            <div className="sign-in-avatar-small">
                                {previewImage || user.picture ? (
                                    <img
                                        src={previewImage || user.picture}
                                        alt="Avatar"
                                        className="sign-in-avatar-image"
                                    />
                                ) : (
                                    user.name?.charAt(0).toUpperCase()
                                )}
                            </div>
                            <span className="sign-in-label">{user.name}</span>
                        </>
                    ) : (
                        <span className="sign-in-label">Sign in</span>
                    )}
                </button>

                {showDropdown && user && (
                    <ProfileDropdown
                        user={user}
                        onProfileClick={handleProfileClick}
                        onLogoutClick={handleLogout}
                        onClose={() => setShowDropdown(false)}
                    />
                )}
            </div>

            {showProfileModal && (
                <ProfileModal
                    user={user}
                    onClose={handleProfileClose}
                    onSave={handleProfileSave}
                    onImageChange={handleImageChange}
                />
            )}

            {deleteConfirmation && createPortal(
                <div className="confirm-modal-overlay" onClick={cancelDelete}>
                    <div className="confirm-modal" onClick={e => e.stopPropagation()}>
                        <div className="confirm-title">Delete this chat?</div>
                        <div className="confirm-actions">
                            <button className="btn-cancel" onClick={cancelDelete}>Cancel</button>
                            <button className="btn-confirm" onClick={confirmDelete}>Delete</button>
                        </div>
                    </div>
                </div>,
                document.body
            )}
        </aside>
    );
}
