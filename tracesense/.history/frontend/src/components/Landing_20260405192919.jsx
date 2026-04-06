export default function Landing({ onStart }) {
  return (
    <div className="landing">

      {/* Background glow orbs */}
      <div className="landing-orb orb1" />
      <div className="landing-orb orb2" />
      <div className="landing-orb orb3" />

      {/* Main content */}
      <div className="landing-content">

        <div className="landing-badge">Semantic Error Correlator</div>

        <h1 className="landing-title">
          Welcome to<br />TraceSense
        </h1>

        <p className="landing-desc">
          Stop hunting through thousands of log lines manually.
          TraceSense understands the <em>meaning</em> of your errors
          and reconstructs the full failure story across every
          microservice — instantly. 

          <em>SAVES YOUR TIME</em>
        </p>

        <div className="landing-features">
          <div className="feature-pill">Semantic Log Correlation</div>
          <div className="feature-pill">Causal Chain Timeline</div>
          <div className="feature-pill">Cross-Service Incidents</div>
        </div>

        <button className="landing-btn" onClick={onStart}>
          Get Started
          <span className="landing-arrow">→</span>
        </button>

        <p className="landing-sub">
          Powered by SBERT · FastAPI · ChromaDB
        </p>

      </div>
    </div>
  );
}