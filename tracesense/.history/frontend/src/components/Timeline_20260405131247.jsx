import { useEffect, useRef } from "react";

const LEVEL_COLOR = {
  ERROR: "#ff4d4d",
  WARN:  "#f5a623",
  INFO:  "#4dff91",
};

const SERVICE_COLORS = {
  "postgres-db":        "#a78bfa",
  "inventory-service":  "#38bdf8",
  "order-service":      "#fb923c",
  "payment-service":    "#4ade80",
  "frontend-service":   "#f472b6",
};

function formatTime(ts) {
  try {
    return new Date(ts).toISOString().split("T")[1].replace("Z", "").slice(0, 12);
  } catch { return ts; }
}

export default function Timeline({ cluster }) {
  const logs = cluster?.incident_cluster || [];
  const canvasRef = useRef(null);

  // get unique services in causal order (by timestamp)
  const sorted = [...logs].sort(
    (a, b) => new Date(a.timestamp) - new Date(b.timestamp)
  );

  const services = [...new Set(sorted.map(l => l.service))];

  // draw connector arrows on canvas overlay
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || sorted.length < 2) return;

    const ctx = canvas.getContext("2d");
    canvas.width  = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // find dot positions from DOM
    sorted.forEach((log, i) => {
      if (i === sorted.length - 1) return;
      const dotA = document.getElementById(`dot-${i}`);
      const dotB = document.getElementById(`dot-${i + 1}`);
      if (!dotA || !dotB) return;

      const rectA   = dotA.getBoundingClientRect();
      const rectB   = dotB.getBoundingClientRect();
      const canRect = canvas.getBoundingClientRect();

      const x1 = rectA.left + rectA.width / 2  - canRect.left;
      const y1 = rectA.top  + rectA.height / 2 - canRect.top;
      const x2 = rectB.left + rectB.width / 2  - canRect.left;
      const y2 = rectB.top  + rectB.height / 2 - canRect.top;

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.bezierCurveTo(x1, (y1 + y2) / 2, x2, (y1 + y2) / 2, x2, y2);
      ctx.strokeStyle = "rgba(167,139,250,0.35)";
      ctx.lineWidth   = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.stroke();

      // arrowhead
      ctx.beginPath();
      ctx.moveTo(x2, y2);
      ctx.lineTo(x2 - 5, y2 - 8);
      ctx.lineTo(x2 + 5, y2 - 8);
      ctx.closePath();
      ctx.fillStyle = "rgba(167,139,250,0.6)";
      ctx.fill();
    });
  }, [logs]);

  if (!logs.length) return null;

  return (
    <div className="timeline-wrap">
      {/* Header */}
      <div className="timeline-header">
        <div className="tl-title">
          Incident Timeline
          <span className="tl-badge">{logs.length} correlated events</span>
        </div>
        <div className="tl-query">
          Query: <em>{cluster.query}</em>
        </div>
      </div>

      {/* Swim Lanes */}
      <div className="swim-container" style={{ position: "relative" }}>
        <canvas
          ref={canvasRef}
          className="connector-canvas"
          style={{
            position: "absolute", top: 0, left: 0,
            width: "100%", height: "100%",
            pointerEvents: "none", zIndex: 2
          }}
        />

        {services.map((service) => {
          const serviceLogs = sorted.filter(l => l.service === service);
          const color = SERVICE_COLORS[service] || "#888";

          return (
            <div className="swim-lane" key={service}>
              {/* Lane label */}
              <div className="lane-label" style={{ borderLeftColor: color }}>
                <span className="lane-dot" style={{ background: color }} />
                <span>{service}</span>
              </div>

              {/* Lane track */}
              <div className="lane-track">
                <div className="lane-line" style={{ borderColor: color + "33" }} />

                {serviceLogs.map((log) => {
                  const globalIndex = sorted.indexOf(log);
                  const levelColor  = LEVEL_COLOR[log.level] || "#888";

                  return (
                    <div className="lane-event" key={globalIndex}>
                      {/* The dot */}
                      <div
                        id={`dot-${globalIndex}`}
                        className="event-dot"
                        style={{
                          background:   levelColor,
                          boxShadow:    `0 0 12px ${levelColor}88`,
                          borderColor:  levelColor,
                        }}
                      />

                      {/* Event card */}
                      <div
                        className="event-card"
                        style={{ borderLeftColor: levelColor }}
                      >
                        <div className="event-card-top">
                          <span
                            className="event-level"
                            style={{ color: levelColor }}
                          >
                            {log.level}
                          </span>
                          <span className="event-time">
                            {formatTime(log.timestamp)}
                          </span>
                          <span className="event-score">
                            {(log.scores?.final * 100).toFixed(0)}% match
                          </span>
                        </div>
                        <div className="event-message">{log.message}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* Root cause banner */}
      <div className="root-cause-banner">
        <span className="rc-label">ROOT CAUSE →</span>
        <span className="rc-service">
          {sorted[0]?.service}
        </span>
        <span className="rc-message">{sorted[0]?.message}</span>
        <span className="rc-time">{formatTime(sorted[0]?.timestamp)}</span>
      </div>
    </div>
  );
}