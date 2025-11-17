import React, { useState } from "react";

export default function Section({ title, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <section className="card">
      <div className="card-header" onClick={() => setOpen(o => !o)}>
        <h3>{title}</h3>
        <span className="chev">{open ? "▾" : "▸"}</span>
      </div>
      {open && <div className="card-body">{children}</div>}
    </section>
  );
}
