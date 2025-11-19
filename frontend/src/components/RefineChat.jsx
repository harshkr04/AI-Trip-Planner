import React, { useEffect, useRef, useState } from "react";

export default function RefineChat({ messages = [], onSend, loading }) {
  const [input, setInput] = useState("");
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSend(input.trim());
    setInput("");
  };

  return (
    <div className="refine-chat card">
      <div className="refine-chat-header">
        <div>
          <p className="eyebrow">Refine Itinerary</p>
          <h3>Ask follow-up questions</h3>
          <p className="muted">Tweak specific days, add budgets, swap activities – your plan updates live.</p>
        </div>
      </div>

      <div className="refine-chat-log" ref={scrollRef}>
        {messages.length === 0 ? (
          <div className="refine-chat-placeholder">
            <p>Ready when you are! Try “Make day 2 more adventurous”.</p>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className={`refine-bubble ${msg.role === "user" ? "user" : "assistant"}`}>
              <span className="refine-role">{msg.role === "user" ? "You" : "Planner"}</span>
              <p>{msg.content}</p>
            </div>
          ))
        )}
      </div>

      <form className="refine-chat-input" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="E.g. Add nightlife on day 3 or swap to budget hotels"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? "Updating..." : "Send"}
        </button>
      </form>
    </div>
  );
}










