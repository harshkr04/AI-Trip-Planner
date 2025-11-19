// Sidebar.jsx
import React, { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import ProfileMenu from "./ProfileMenu";
import ConfirmModal from "./ConfirmModal";
import Toast from "./Toast";
import "./Sidebar.css";

export default function Sidebar({
  sessions = [],
  onLoadSession = () => {},
  onNewChat = () => {},
  isMobileOpen = false,
  onCloseMobile = () => {},
}) {
  const [remoteSessions, setRemoteSessions] = useState([]);
  const [deletingId, setDeletingId] = useState(null);
  const [deletedSession, setDeletedSession] = useState(null);
  const [toast, setToast] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [confirmState, setConfirmState] = useState({
    open: false,
    id: null,
    title: "",
    loading: false,
    error: null,
  });

  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    let mounted = true;
    const API_BASE = process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '';
    fetch(`${API_BASE}/api/sessions/`)
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

  const filteredSessions = useMemo(() => {
    if (!searchTerm.trim()) return mergedSessions;
    const term = searchTerm.toLowerCase();
    return mergedSessions.filter((s) => {
      const title = s?.title || s?.prompt || "";
      return title.toLowerCase().includes(term);
    });
  }, [mergedSessions, searchTerm]);

  function shortSummary(text) {
    if (!text) return "";
    const words = text.trim().split(/\s+/);
    return words.slice(0, 6).join(" ") + (words.length > 6 ? "…" : "");
  }

  function handleLoadSession(s) {
    onLoadSession(s);
    if (location.pathname !== "/") navigate("/");
    onCloseMobile();
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

    // Store the session for potential undo
    const sessionToDelete = [...remoteSessions, ...sessions].find(s => String(s?.id) === String(id));
    
    try {
      const API_BASE = process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '';
      const resp = await fetch(`${API_BASE}/api/history/${encodeURIComponent(id)}`, { 
        method: "DELETE",
        headers: { "Content-Type": "application/json" }
      });
      if (!resp.ok) {
        const text = await resp.text().catch(() => "");
        let message = "Failed to delete chat";
        try {
          const parsed = JSON.parse(text);
          if (parsed?.detail) {
            message = parsed.detail;
          } else if (typeof parsed === "string") {
            message = parsed;
          }
        } catch {
          if (text) message = text;
        }
        throw new Error(message);
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
      
      // Show toast with undo
      if (sessionToDelete) {
        setDeletedSession(sessionToDelete);
        setToast({ message: "Chat deleted", onUndo: handleUndoDelete });
      }
    } catch (err) {
      setConfirmState((s) => ({ ...s, loading: false, error: err.message || "Delete failed" }));
    } finally {
      setDeletingId(null);
    }
  }

  function handleUndoDelete() {
    if (!deletedSession) return;
    
    // Restore to localStorage
    try {
      const raw = localStorage.getItem("ai_chat_sessions");
      const arr = raw ? JSON.parse(raw) : [];
      if (!arr.find(s => String(s.id) === String(deletedSession.id))) {
        arr.unshift(deletedSession);
        localStorage.setItem("ai_chat_sessions", JSON.stringify(arr.slice(0, 20)));
      }
    } catch (e) {
      // ignore
    }
    
    // Restore to remote sessions
    setRemoteSessions((rs) => {
      if (!rs.find(s => String(s.id) === String(deletedSession.id))) {
        return [deletedSession, ...rs];
      }
      return rs;
    });
    
    setDeletedSession(null);
    setToast(null);
  }

  const sidebarClasses = ["sidebar-root"];
  if (isMobileOpen) sidebarClasses.push("sidebar-open");

  return (
    <aside className={sidebarClasses.join(" ")} aria-label="Sidebar">
      <div className="sidebar-column">
        <div className="sidebar-top">
          <button
            className="btn-new"
            onClick={() => {
              onNewChat();
              if (location.pathname !== "/") navigate("/");
              onCloseMobile();
            }}
          >
            + New Chat
          </button>
          <div className="sidebar-search">
            <input
              type="text"
              placeholder="Search chats"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              aria-label="Search chats"
            />
          </div>
        </div>

        <div className="sidebar-section history-wrap">
          <div className="sidebar-title">Chat History</div>

          <div className="history" role="list" aria-label="Chat history" tabIndex={0}>
            {filteredSessions.length === 0 ? (
              <div className="empty">No matching chats.</div>
            ) : (
              filteredSessions.map((s) => {
                const id = s?.id ?? Math.random().toString(36).slice(2, 9);
                const title = s?.title || s?.prompt || "Trip";
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
                    title={title}
                  >
                    <div className="chat-body" title={title}>
                      <div className="chat-title">{shortSummary(title)}</div>
                    </div>

                    <div className="chat-actions">
                      <span className="chat-view" aria-hidden="true">
                        View
                      </span>
                      <button
                        type="button"
                        className="chat-delete"
                        aria-label={`Delete chat ${title.slice(0, 40)}`}
                        title="Delete chat"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteClick(id, title);
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
                  </div>
                );
              })
            )}
          </div>
        </div>

        <div className="sidebar-section navigation">
          <div className="sidebar-title">Navigation</div>

          <nav className="nav-list" aria-label="Main navigation">
            <Link
              to="/flights"
              className={`nav-link ${location.pathname === "/flights" ? "active" : ""}`}
              onClick={onCloseMobile}
            >
              <span className="nav-ico">✈️</span>
              <span className="nav-text">Flight Search</span>
            </Link>

            <hr className="sub-divider" />

            <Link
              to="/hotels"
              className={`nav-link ${location.pathname === "/hotels" ? "active" : ""}`}
              onClick={onCloseMobile}
            >
              <span className="nav-ico">🏨</span>
              <span className="nav-text">Hotels & Cuisines</span>
            </Link>

            <hr className="sub-divider" />

            <Link
              to="/news"
              className={`nav-link ${location.pathname === "/news" ? "active" : ""}`}
              onClick={onCloseMobile}
            >
              <span className="nav-ico">📰</span>
              <span className="nav-text">Travel News & Blogs</span>
            </Link>
          </nav>
        </div>

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

      {toast && (
        <Toast
          message={toast.message}
          onUndo={toast.onUndo}
          onClose={() => {
            setToast(null);
            setDeletedSession(null);
          }}
        />
      )}
      <button
        className="sidebar-close"
        type="button"
        aria-label="Close sidebar"
        onClick={onCloseMobile}
      >
        ×
      </button>
    </aside>
  );
}
