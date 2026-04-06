export default function QueryPanel({
  query, setQuery, timestamp, setTimestamp,
  onCorrelate, onDemo, loading
}) {
  return (
    <div className="query-panel">
      <div className="panel-label">INCIDENT QUERY</div>

      <textarea
        className="query-input"
        placeholder="Paste any error message here...&#10;e.g. payment failed code=402 checkout failed"
        value={query}
        onChange={e => setQuery(e.target.value)}
        rows={4}
      />

      <div className="ts-row">
        <label className="ts-label">Timestamp (ISO)</label>
        <input
          className="ts-input"
          placeholder="2026-04-05T11:47:09.002Z"
          value={timestamp}
          onChange={e => setTimestamp(e.target.value)}
        />
        <button
          className="now-btn"
          onClick={() => setTimestamp(new Date().toISOString())}
        >
          Now
        </button>
      </div>

      <div className="btn-row">
        <button className="demo-btn" onClick={onDemo}>
          Load Demo
        </button>
        <button
          className="correlate-btn"
          onClick={onCorrelate}
          disabled={loading || !query.trim()}
        >
          {loading ? "Correlating..." : "⬡ Correlate"}
        </button>
      </div>

      <div className="hint-box">
        <strong>How to use:</strong>
        <ol>
          <li>Run <code>python simulator/log_generator.py</code></li>
          <li>Click <em>Load Demo</em> or paste your own error</li>
          <li>Hit <em>Correlate</em> to reconstruct the incident</li>
        </ol>
      </div>
    </div>
  );
}