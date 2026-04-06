import { useState, useEffect } from "react";
import axios from "axios";
import Timeline from "./components/Timeline";
import QueryPanel from "./components/QueryPanel";
import LogFeed from "./components/LogFeed";
import "./App.css";

const API = "http://localhost:8000";

export default function App() {
  const [query, setQuery] = useState("");
  const [timestamp, setTimestamp] = useState("");
  const [cluster, setCluster] = useState(null);
  const [loading, setLoading] = useState(false);
  const [logCount, setLogCount] = useState(0);
  const [error, setError] = useState(null);
  const [simulatorRunning, setSimulatorRunning] = useState(false);

  useEffect(() => {
    fetchLogCount();
    const interval = setInterval(fetchLogCount, 5000);
    return () => clearInterval(interval);
  }, []);

  async function fetchLogCount() {
    try {
      const res = await axios.get(`${API}/logs/count`);
      setLogCount(res.data.total_logs_stored);
    } catch {
      // backend not reachable yet
    }
  }

  async function runCorrelation() {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setCluster(null);

    const ts = timestamp || new Date().toISOString();

    try {
      const res = await axios.post(`${API}/correlate`, {
        message: query,
        timestamp: ts,
      });
      setCluster(res.data);
    } catch (e) {
      setError("Could not reach backend. Make sure uvicorn is running on :8000");
    } finally {
      setLoading(false);
    }
  }

  function handleDemo() {
    setQuery("payment failed code=402 checkout failed");
    setTimestamp("2026-04-05T11:47:09.002Z");
  }

  return (
    <div className="app">
      {/* Top Bar */}
      <header className="topbar">
        <div className="topbar-left">
          <span className="logo-icon">⬡</span>
          <span className="logo-text">TraceSense</span>
          <span className="logo-sub">Semantic Error Correlator</span>
        </div>
        <div className="topbar-right">
          <div className="stat-pill">
            <span className="stat-dot pulse" />
            <span>{logCount.toLocaleString()} logs indexed</span>
          </div>
          <div className="status-pill">
            <span className="status-dot" />
            <span>Active</span>
          </div>
        </div>
      </header>

      <div className="layout">
        {/* Left Panel */}
        <aside className="left-panel">
          <QueryPanel
            query={query}
            setQuery={setQuery}
            timestamp={timestamp}
            setTimestamp={setTimestamp}
            onCorrelate={runCorrelation}
            onDemo={handleDemo}
            loading={loading}
          />
          {cluster && (
            <LogFeed cluster={cluster} />
          )}
        </aside>

        {/* Main Timeline */}
        <main className="main-panel">
          {!cluster && !loading && (
            <div className="empty-state">
              <div className="empty-icon">⬡</div>
              <h2>No incident loaded</h2>
              <p>
                Run the simulator first, then paste any error message into
                the query box and hit Correlate.
              </p>
              <button className="demo-hint" onClick={handleDemo}>
                Load demo query →
              </button>
            </div>
          )}
          {loading && (
            <div className="empty-state">
              <div className="spinner" />
              <p>Correlating across services...</p>
            </div>
          )}
          {error && (
            <div className="empty-state error-state">
              <p>{error}</p>
            </div>
          )}
          {cluster && !loading && (
            <Timeline cluster={cluster} />
          )}
        </main>
      </div>
    </div>
  );
}