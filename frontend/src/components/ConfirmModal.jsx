// ConfirmModal.jsx
import React from "react";
import "./Sidebar.css"; // modal styles are included there

export default function ConfirmModal({
  open = false,
  title = "Confirm",
  message = "",
  loading = false,
  error = null,
  confirmLabel = "OK",
  cancelLabel = "Cancel",
  onConfirm = () => {},
  onCancel = () => {},
}) {
  if (!open) return null;

  return (
    <div className="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
      <div className="modal-card">
        <h3 id="confirm-title" className="modal-title">{title}</h3>
        <div className="modal-body">
          {error ? (
            <div style={{ color: "#b91c1c", fontWeight: 600, marginBottom: 8 }}>{error}</div>
          ) : null}
          <div>{message}</div>
        </div>

        <div className="modal-actions">
          <button
            type="button"
            className="modal-btn modal-cancel"
            onClick={onCancel}
            disabled={loading}
          >
            {cancelLabel}
          </button>

          <button
            type="button"
            className="modal-btn modal-confirm"
            onClick={onConfirm}
            disabled={loading}
            aria-busy={loading}
          >
            {loading ? "Deleting..." : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
