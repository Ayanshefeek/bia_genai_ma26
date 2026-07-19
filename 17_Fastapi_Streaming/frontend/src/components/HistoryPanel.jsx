export default function HistoryPanel({ runs, onRefresh }) {
  return (
    <section className="card">
      <div className="section-heading inline-heading">
        <div>
          <span className="eyebrow">SQLite history</span>
          <h2>Recent runs</h2>
        </div>
        <button className="secondary-button" onClick={onRefresh}>Refresh</button>
      </div>

      <div className="history-list">
        {runs.length === 0 && <p className="muted">No runs yet. Trigger an event first.</p>}

        {runs.map((run) => (
          <article key={run.id} className="history-item">
            <div>
              <span className="run-id">{run.id}</span>
              <h3>{run.title}</h3>
              <p>{run.event_type} · {run.priority} · {run.status}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
