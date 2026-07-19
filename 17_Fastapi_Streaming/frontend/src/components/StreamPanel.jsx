export default function StreamPanel({ status, activeRunId, streamedText, messages }) {
  return (
    <section className="card stream-card">
      <div className="section-heading">
        <span className="eyebrow">Live assistant stream</span>
        <h2>{activeRunId ? `Watching ${activeRunId}` : "No active run yet"}</h2>
      </div>

      <div className={`status-badge ${status}`}>{status || "idle"}</div>

      <div className="stream-output">
        {streamedText ? streamedText : "Trigger an event to see the assistant response stream here."}
      </div>

      <details>
        <summary>Raw WebSocket messages</summary>
        <pre className="raw-log">{messages.map((message) => JSON.stringify(message)).join("\n")}</pre>
      </details>
    </section>
  );
}
