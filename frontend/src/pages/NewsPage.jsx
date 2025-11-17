// frontend/src/pages/NewsPage.jsx
import React, { useState, useEffect } from "react";
import { fetchNews } from "../api/news";
import Section from "../components/Section";

export default function NewsPage() {
  const [query, setQuery] = useState("travel");
  const [loading, setLoading] = useState(false);
  const [articles, setArticles] = useState([]);
  const [error, setError] = useState("");

  const loadNews = async (q = "travel") => {
    setLoading(true);
    try {
      const res = await fetchNews(q);
      const data = res.data || res;
      setArticles(data.articles || data || []);
      setError("");
    } catch (e) {
      console.error(e);
      setError("Failed to fetch news.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNews(query);
  }, []);

  return (
    <div>
      <h2 style={{ marginTop: 6 }}>Travel News & Blogs</h2>

      <div style={{ display: "flex", gap: 12, marginTop: 12, marginBottom: 18 }}>
        <input className="input" placeholder="Search topic (e.g., 'Manali travel')" value={query} onChange={e => setQuery(e.target.value)} style={{ width: 320 }} />
        <button className="btn-send" onClick={() => loadNews(query)} disabled={loading}>
          {loading ? "Searching..." : "Search News"}
        </button>
      </div>

      <Section title="Latest Articles" defaultOpen={true}>
        {error && <div className="empty">{error}</div>}
        {articles.length === 0 ? <div className="empty">No articles found.</div> : (
          <div className="list">
            {articles.map((a, idx) => (
              <div key={idx} className="list-row" style={{ alignItems: "flex-start" }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700 }}>{a.title}</div>
                  <div className="muted" style={{ marginTop: 6 }}>{a.source?.name || a.author || ""} • {new Date(a.publishedAt || Date.now()).toLocaleDateString()}</div>
                  <div style={{ marginTop: 8 }}>{a.description}</div>
                  <a href={a.url} target="_blank" rel="noreferrer" style={{ marginTop: 8, display: "inline-block" }}>Read full article ↗</a>
                </div>
              </div>
            ))}
          </div>
        )}
      </Section>
    </div>
  );
}
