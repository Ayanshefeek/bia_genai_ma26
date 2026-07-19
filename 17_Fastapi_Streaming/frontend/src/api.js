const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function getHealth() {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) throw new Error("Backend health check failed.");
  return response.json();
}

export async function getSampleEvents() {
  const response = await fetch(`${API_BASE_URL}/api/sample-events`);
  if (!response.ok) throw new Error("Could not fetch sample events.");
  return response.json();
}

export async function triggerEvent(eventPayload) {
  const response = await fetch(`${API_BASE_URL}/api/trigger`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(eventPayload)
  });
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Trigger failed: ${errorText}`);
  }
  return response.json();
}

export async function getRuns() {
  const response = await fetch(`${API_BASE_URL}/api/runs`);
  if (!response.ok) throw new Error("Could not fetch run history.");
  return response.json();
}

export async function resetDemoData() {
  const response = await fetch(`${API_BASE_URL}/api/reset`, { method: "POST" });
  if (!response.ok) throw new Error("Could not reset demo data.");
  return response.json();
}

export function websocketUrlForRun(runId) {
  const wsBase = API_BASE_URL.replace("http://", "ws://").replace("https://", "wss://");
  return `${wsBase}/ws/runs/${runId}`;
}
