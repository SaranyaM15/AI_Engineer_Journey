const LEVEL_COLOR = {
  ERROR: "#ff4d4d",
  WARN:  "#f5a623",
  INFO:  "#4dff91",
};

const SERVICE_ICONS = {
  "postgres-db":        "🗄",
  "inventory-service":  "📦",
  "order-service":      "📋",
  "payment-service":    "💳",
  "frontend-service":   "🖥",
};

function formatTime(ts) {
  try {
    const d = new Date(ts);
    return d.toISOString().split("T")[1].replace("Z", "").slice(0, 12);
  } catch {
    return ts;
  }
}

export default function LogFeed({ cluster }) {
  const logs = cluster?.incident_cluster || [];

  return (
    <div className="log-feed">
      <div className="panel-label">
        CORRELATED EVENTS
        <span className="count-badge">{logs.length}</span>
      </div>

      <div className="log-list">
        {logs.map((log, i) => (
          <div className="log-card" key={i}>
            <div className="log-card-top">
              <span className="log-icon">
                {SERVICE_ICONS[log.service] || "⬡"}
              </span>
              <span
                className="log-level"
                style={{ color: LEVEL_COLOR[log.level] || "#aaa" }}
              >
                {log.level}
              </span>
              <span className="log-service">{log.service}</span>
              <span className="log-score">
                {(log.scores?.final * 100).toFixed(0)}%
              </span>
            </div>

            <div className="log-message">{log.message}</div>

            <div className="log-meta">
              <span>{formatTime(log.timestamp)}</span>
              <div className="score-bars">
                <span title="semantic">
                  S:{(log.scores?.semantic * 100).toFixed(0)}
                </span>
                <span title="temporal">
                  T:{(log.scores?.temporal * 100).toFixed(0)}
                </span>
              </div>
            </div>

            {/* confidence bar */}
            <div className="conf-bar-bg">
              <div
                className="conf-bar-fill"
                style={{ width: `${(log.scores?.final || 0) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}