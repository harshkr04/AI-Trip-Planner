// frontend/src/components/DeleteConfirmModal.jsx
import React from "react";
import "./Sidebar.css"; // modal CSS is included here for convenience

export default function DeleteConfirmModal({ open = false, title = "", onConfirm = () => {}, onCancel = () => {} }) {
  if (!open) return null;

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-label="Confirm delete">
      <div className="modal-card">
        <h3 className="modal-title">Delete chat?</h3>
        <p className="modal-body">{title ? `Delete "${title}"? This cannot be undone.` : "Delete this chat? This cannot be undone."}</p>

        <div className="modal-actions">
          <button className="modal-btn modal-cancel" onClick={onCancel}>Cancel</button>
          <button className="modal-btn modal-confirm" onClick={onConfirm}>Delete</button>
        </div>
      </div>
    </div>
  );
}
