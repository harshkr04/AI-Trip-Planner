// Sidebar.jsx
import React, { useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import ProfileMenu from "./ProfileMenu";
import ConfirmModal from "./ConfirmModal";
import "./Sidebar.css";

export default function Sidebar({
  sessions = [],
  onLoadSession = () => {},
  onNewChat = () => {},
}) {
  const [remoteSessions, setRemoteSessions] = useState([]);
  const [deletingId, setDeletingId] = useState(null);
  const [confirmState, setConfirmState] = useState({
    open: false,
    id: null,
    title: "",
    loading: false,
    error: null,
  });

  const location = useLocation();
  const navigate = useNavigate();
  const scrollableRef = useRef(null);

  useEffect(() => {
    let mounted = true;
    fetch("/api/sessions/list")
      .then((r) => (r.ok ? r.json() : []))
      .then((data) => {
        if (!mounted) return;
        if (Array.isArray(data)) setRemoteSessions(data);
      })
      .catch(() => {
        if (!mounted) return;
        setRemoteSessions([]);
      });
    return () => (mounted = false);
  }, []);

  const mergedSessions = useMemo(() => {
    const map = new Map();
    (sessions || []).forEach((s) => {
      if (s && s.id) map.set(String(s.id), s);
    });
    (remoteSessions || []).forEach((rs) => {
      if (rs && rs.id && !map.has(String(rs.id))) map.set(String(rs.id), rs);
    });
    return Array.from(map.values()).slice(0, 40);
  }, [sessions, remoteSessions]);

  function shortSummary(text) {
    if (!text) return "";
    const words = text.trim().split(/\s+/);
    return words.slice(0, 6).join(" ") + (words.length > 6 ? "…" : "");
  }

  function handleLoadSession(s) {
    onLoadSession(s);
    if (location.pathname !== "/") navigate("/");
  }

  function onDeleteClick(id, title) {
    setConfirmState({ open: true, id, title: title || "", loading: false, error: null });
  }
  function closeConfirm() {
    setConfirmState({ open: false, id: null, title: "", loading: false, error: null });
  }

  async function handleConfirmDelete() {
    const id = confirmState.id;
    if (!id) return;
    setConfirmState((s) => ({ ...s, loading: true, error: null }));
    setDeletingId(id);

    try {
      const resp = await fetch(`/api/sessions/${encodeURIComponent(id)}`, { method: "DELETE" });
      if (!resp.ok) {
        const text = await resp.text().catch(() => "Failed to delete session");
        throw new Error(text || "Failed to delete session");
      }

      setRemoteSessions((rs) => rs.filter((r) => String(r.id) !== String(id)));

      try {
        const raw = localStorage.getItem("ai_chat_sessions");
        if (raw) {
          const arr = JSON.parse(raw);
          const filtered = arr.filter((x) => String(x.id) !== String(id));
          localStorage.setItem("ai_chat_sessions", JSON.stringify(filtered));
        }
      } catch (e) {
        // ignore localStorage errors
      }

      setConfirmState({ open: false, id: null, title: "", loading: false, error: null });
    } catch (err) {
      setConfirmState((s) => ({ ...s, loading: false, error: err.message || "Delete failed" }));
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <aside className="sidebar-root" aria-label="Sidebar">
      <div className="sidebar-column">
        {/* top - New Chat */}
        <div className="sidebar-top">
          <button
            className="btn-new"
            onClick={() => {
              onNewChat();
              if (location.pathname !== "/") navigate("/");
            }}
          >
            + New Chat
          </button>
        </div>

        {/* middle scrollable group: chat history + navigation */}
        <div className="sidebar-middle" ref={scrollableRef}>
          <div className="sidebar-section">
            <div className="sidebar-title">Chat History</div>

            <div className="history"
                 role="list"
                 aria-label="Chat history"
                 tabIndex={0}
                 /* scroll snap container */
            >
              {mergedSessions.length === 0 ? (
                <div className="empty">No saved chats yet</div>
              ) : (
                mergedSessions.map((s) => {
                  const id = s?.id ?? Math.random().toString(36).slice(2, 9);
                  return (
                    <div
                      key={id}
                      role="listitem"
                      className="item chat-row"
                      tabIndex={0}
                      onClick={() => handleLoadSession(s)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          handleLoadSession(s);
                        }
                      }}
                    >
                      <div className="chat-body">
                        <div className="chat-title">{shortSummary(s.title || s.prompt || "Trip")}</div>
                        <div className="chat-sub">{s.createdAt ? new Date(s.createdAt).toLocaleString() : (s.created || "")}</div>
                      </div>

                      <button
                        type="button"
                        className="chat-delete"
                        aria-label={`Delete chat ${s.title ? s.title.slice(0, 40) : ""}`}
                        title="Delete chat"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteClick(id, s.title || s.prompt || "");
                        }}
                        disabled={deletingId === id}
                      >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
                          <path d="M3 6h18" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                          <path d="M8 6v12a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2V6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                          <path d="M10 11v6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                          <path d="M14 11v6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                          <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </button>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* small separator */}
          <hr className="divider" />

          <div className="sidebar-section">
            <div className="sidebar-title">Navigation</div>

            <nav className="nav-list" aria-label="Main navigation">
              <Link to="/flights" className={`nav-link ${location.pathname === "/flights" ? "active" : ""}`}>
                <span className="nav-ico">✈️</span>
                <span className="nav-text">Flight Search</span>
              </Link>

              <hr className="sub-divider" />

              <Link to="/hotels" className={`nav-link ${location.pathname === "/hotels" ? "active" : ""}`}>
                <span className="nav-ico">🏨</span>
                <span className="nav-text">Hotels & Cuisines</span>
              </Link>

              <hr className="sub-divider" />

              <Link to="/news" className={`nav-link ${location.pathname === "/news" ? "active" : ""}`}>
                <span className="nav-ico">📰</span>
                <span className="nav-text">Travel News & Blogs</span>
              </Link>
            </nav>
          </div>
        </div>

        {/* footer - pinned bottom */}
        <div className="sidebar-footer">
          <ProfileMenu />
        </div>
      </div>

      <ConfirmModal
        open={confirmState.open}
        title="Permanently delete this chat?"
        message={
          confirmState.error
            ? `${confirmState.error}`
            : `Delete "${(confirmState.title || "this chat").slice(0, 60)}"? This cannot be undone.`
        }
        loading={confirmState.loading}
        error={confirmState.error}
        confirmLabel="Delete"
        cancelLabel="Cancel"
        onConfirm={handleConfirmDelete}
        onCancel={closeConfirm}
      />
    </aside>
  );
}
