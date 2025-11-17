// frontend/src/components/ItinerarySection.jsx
import React, { useState } from "react";
import { downloadPdf } from "../api/pdf";

/**
 * Small markdown-lite renderer used to show LLM itinerary cleanly.
 */
function renderItineraryLines(itineraryText) {
  if (!itineraryText) return null;
  const lines = itineraryText.split("\n");
  const blocks = [];
  let currentList = null;

  const pushListIfAny = () => {
    if (currentList) {
      blocks.push({ type: "list", items: currentList });
      currentList = null;
    }
  };

  const boldify = (s) => s.replace(/\*\*(.+?)\*\*/g, (_, m) => `<strong>${m}</strong>`);

  lines.forEach((raw) => {
    const line = raw.trim();
    if (!line) {
      pushListIfAny();
      return;
    }
    if (line.startsWith("## ")) {
      pushListIfAny();
      blocks.push({ type: "h3", text: boldify(line.substring(3)) });
      return;
    }
    if (line.startsWith("# ")) {
      pushListIfAny();
      blocks.push({ type: "h2", text: boldify(line.substring(2)) });
      return;
    }
    if (/^[-*]\s+/.test(line)) {
      const text = line.replace(/^[-*]\s+/, "");
      if (!currentList) currentList = [];
      currentList.push(boldify(text));
      return;
    }
    pushListIfAny();
    blocks.push({ type: "p", text: boldify(line) });
  });

  pushListIfAny();
  return blocks;
}

export default function ItinerarySection({ itinerary }) {
  const [downloading, setDownloading] = useState(false);
  if (!itinerary) return null;
  const blocks = renderItineraryLines(itinerary);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      await downloadPdf({ title: "Trip Itinerary", itinerary });
      alert("PDF download requested — check your downloads.");
    } catch (e) {
      console.error(e);
      alert("PDF generation failed.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3>📋 Day-by-Day Itinerary</h3>
        <button className="btn-download" onClick={handleDownload} disabled={downloading}>
          {downloading ? "⏳ Generating..." : "📥 Download PDF"}
        </button>
      </div>

      <div className="card-body itinerary-body">
        {blocks.map((b, i) => {
          if (b.type === "h2") {
            return <h2 key={i} className="itinerary-heading" dangerouslySetInnerHTML={{ __html: b.text }} />;
          }
          if (b.type === "h3") {
            return <h3 key={i} className="itinerary-subheading" dangerouslySetInnerHTML={{ __html: b.text }} />;
          }
          if (b.type === "list") {
            return (
              <ul key={i} style={{ marginLeft: 24, marginBottom: 12 }}>
                {b.items.map((it, j) => (
                  <li key={j} className="itinerary-bullet" dangerouslySetInnerHTML={{ __html: it }} />
                ))}
              </ul>
            );
          }
          return <p key={i} className="itinerary-line" dangerouslySetInnerHTML={{ __html: b.text }} />;
        })}
      </div>
    </div>
  );
}
