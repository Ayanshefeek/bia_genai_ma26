export default function EventSimulator({
  sampleEvents,
  selectedIndex,
  setSelectedIndex,
  onTrigger,
  isLoading
}) {
  const selectedEvent = sampleEvents[selectedIndex] || null;

  return (
    <section className="card">
      <div className="section-heading">
        <span className="eyebrow">Mock trigger</span>
        <h2>Simulate a productivity event</h2>
      </div>

      <div className="event-buttons">
        {sampleEvents.map((event, index) => (
          <button
            key={event.title}
            className={index === selectedIndex ? "pill active" : "pill"}
            onClick={() => setSelectedIndex(index)}
          >
            {event.event_type}
          </button>
        ))}
      </div>

      {selectedEvent && (
        <div className="event-preview">
          <p className="priority">Priority: {selectedEvent.priority}</p>
          <h3>{selectedEvent.title}</h3>
          <pre>{JSON.stringify(selectedEvent.payload, null, 2)}</pre>
        </div>
      )}

      <button
        className="primary-button"
        onClick={() => selectedEvent && onTrigger(selectedEvent)}
        disabled={!selectedEvent || isLoading}
      >
        {isLoading ? "Triggering..." : "Trigger event and stream response"}
      </button>
    </section>
  );
}
