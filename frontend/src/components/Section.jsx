import React, { useState } from "react";

export default function Section({ title, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="card">
      <div className="card-header" onClick={() => setOpen(!open)}>
        <h3>{title}</h3>
        <span>{open ? "▾" : "▸"}</span>
      </div>
      {open && <div className="card-body">{children}</div>}
    </div>
  );
}
