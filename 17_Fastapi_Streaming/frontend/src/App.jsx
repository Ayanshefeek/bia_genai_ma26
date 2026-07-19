import React, { useEffect, useRef, useState } from "react";
import EventSimulator from "./components/EventSimulator.jsx";
import StreamPanel from "./components/StreamPanel.jsx";
import HistoryPanel from "./components/HistoryPanel.jsx";
import {
  getHealth,
  getRuns,
  getSampleEvents,
  resetDemoData,
  triggerEvent,
  websocketUrlForRun
} from "./api.js";
import "./styles.css";

export default function App() {
  const [health, setHealth] = useState(null);
  const [sampleEvents, setSampleEvents] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [runs, setRuns] = useState([]);
  const [activeRunId, setActiveRunId] = useState("");
  const [streamedText, setStreamedText] = useState("");
  const [messages, setMessages] = useState([]);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const socketRef = useRef(null);

  async function refreshRuns() {
    const recentRuns = await getRuns();
    setRuns(recentRuns);
  }

  useEffect(() => {
    async function loadInitialData() {
      try {
        setHealth(await getHealth());
        setSampleEvents(await getSampleEvents());
        await refreshRuns();
      } catch (err) {
        setError(err.message);
      }
    }
    loadInitialData();
  }, []);

  function connectToRun(runId) {
    if (socketRef.current) {
      socketRef.current.close();
    }

    setActiveRunId(runId);
    setStreamedText("");
    setMessages([]);
    setStatus("connecting");

    const socket = new WebSocket(websocketUrlForRun(runId));
    socketRef.current = socket;

    socket.onopen = () => {
      setStatus("connected");
      socket.send("ping");
    };

    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setMessages((existing) => [...existing, message]);

      if (message.type === "status") {
        setStatus(message.status);
      }

      if (message.type === "token") {
        setStreamedText((existing) => existing + message.content);
      }

      if (message.type === "done") {
        setStatus("completed");
        refreshRuns();
      }

      if (message.type === "error") {
        setStatus("failed");
        setError(message.message || "Streaming failed.");
      }
    };

    socket.onerror = () => {
      setStatus("failed");
      setError("WebSocket connection failed. Check that the backend is running.");
    };

    socket.onclose = () => {
      if (status !== "completed") {
        setStatus((current) => (current === "failed" ? "failed" : "closed"));
      }
    };
  }

  async function handleTrigger(eventPayload) {
    try {
      setError("");
      setStatus("triggering");
      const response = await triggerEvent(eventPayload);
      connectToRun(response.run_id);
      await refreshRuns();
    } catch (err) {
      setError(err.message);
      setStatus("failed");
    }
  }

  async function handleReset() {
    await resetDemoData();
    setRuns([]);
    setStreamedText("");
    setMessages([]);
    setActiveRunId("");
    setStatus("idle");
    setError("");
  }

  return (
    <main className="app-shell">
      <header className="hero">
        <div>
          <span className="eyebrow">Real-time agent practical</span>
          <h1>Streaming Productivity Assistant</h1>
          <p>
            Mock Gmail/Calendar/task events trigger an assistant run. The backend stores
            state in SQLite and streams response chunks live to this React dashboard.
          </p>
        </div>
        <div className="health-card">
          <span>Backend</span>
          <strong>{health ? health.status : "checking..."}</strong>
          <small>{health ? `${health.llm_mode} · ${health.model}` : "Start FastAPI first"}</small>
          <button className="secondary-button" onClick={handleReset}>Reset demo data</button>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="grid">
        <EventSimulator
          sampleEvents={sampleEvents}
          selectedIndex={selectedIndex}
          setSelectedIndex={setSelectedIndex}
          onTrigger={handleTrigger}
          isLoading={status === "triggering"}
        />
        <StreamPanel
          status={status}
          activeRunId={activeRunId}
          streamedText={streamedText}
          messages={messages}
        />
      </div>

      <HistoryPanel runs={runs} onRefresh={refreshRuns} />
    </main>
  );
}
