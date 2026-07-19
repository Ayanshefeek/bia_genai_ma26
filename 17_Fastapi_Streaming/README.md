# Streaming Productivity Assistant

A practical full-stack build for real-time, event-driven agents: mock Gmail/Calendar/task events trigger a FastAPI backend, the assistant streams text chunks through WebSockets, a React dashboard displays the live response, and SQLite preserves events, runs, and streamed chunks.

## Prerequisites

- Python 3.10 or 3.11
- Node.js 20+ for the React dashboard
- VS Code or another editor
- Optional: OpenAI API key for live model streaming
- Works on Windows, macOS, and Linux

The full demo runs in mock LLM mode by default, so an API key is not required for the first classroom run.

## Setup

### 1. Download or open the project

Open a terminal in the `streaming_productivity_assistant` folder.

### 2. Create a Python virtual environment

Using `venv`:

```bash
python -m venv .venv
```

Activate it:

Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Using conda instead:

```bash
conda create -n streaming-productivity-assistant python=3.11
conda activate streaming-productivity-assistant
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.sample` to `.env`.

Windows PowerShell:

```bash
Copy-Item .env.sample .env
```

macOS/Linux:

```bash
cp .env.sample .env
```

Default classroom mode:

```env
APP_USE_MOCK_LLM=true
```

To use live OpenAI streaming:

```env
APP_USE_MOCK_LLM=false
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 5. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

## How to run

### Option A — full app demo

Terminal 1: start the backend from the project root.

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

Terminal 2: start the React dashboard.

```bash
cd frontend
npm run dev
```

Open the dashboard, normally:

```text
http://127.0.0.1:5173
```

In the dashboard:

1. Pick one mock event: email, calendar, or task.
2. Click **Trigger event and stream response**.
3. Watch the assistant response stream into the live panel.
4. Refresh recent runs to show SQLite-persisted run history.

### Option B — notebook walkthrough

Start Jupyter from the project root and open `notebook.ipynb`.

```bash
jupyter notebook
```

Run all cells. The notebook demonstrates:

- sample event structure
- prompt construction
- mock token streaming
- SQLite event/run persistence
- an end-to-end backend processing call without opening the React UI

### Option C — backend API only

Trigger a sample-like event with curl:

```bash
curl -X POST http://127.0.0.1:8000/api/trigger \
  -H "Content-Type: application/json" \
  -d "{\"event_type\":\"email\",\"title\":\"Client asks for a status update\",\"source\":\"mock\",\"priority\":\"high\",\"payload\":{\"from\":\"client@example.com\",\"body\":\"Please send a quick update.\"}}"
```

Use the returned `run_id` to connect from the dashboard or a WebSocket client.

## What each file does

```text
backend/main.py                  FastAPI routes, WebSocket endpoint, background run processor
backend/agent.py                 OpenAI/mock assistant streaming logic
backend/connection_manager.py    In-memory run_id → WebSocket client manager
backend/database.py              SQLite schema and persistence functions
backend/mock_events.py           Ready-to-trigger email, calendar, and task examples
backend/schemas.py               Pydantic request/response models
backend/tests/                   API and WebSocket replay tests
frontend/src/App.jsx             Main React dashboard
frontend/src/api.js              REST and WebSocket helper functions
frontend/src/components/         UI components for event trigger, stream panel, run history
data/sample_events.json          JSON version of classroom demo events
notebook.ipynb                   Guided practical walkthrough
.env.sample                      Environment variable template
requirements.txt                 Pinned Python dependencies
trainer_guide.md                 Detailed trainer delivery guide
```

## Expected output

Backend health check:

```json
{
  "status": "ok",
  "app_name": "Streaming Productivity Assistant",
  "llm_mode": "mock",
  "model": "gpt-4o-mini"
}
```

Dashboard behaviour:

- Backend health card shows `ok`
- Three mock event buttons appear
- Triggering an event creates an event ID and run ID
- The stream panel fills progressively instead of waiting for the full response
- Recent runs appear with event type, priority, and run status

SQLite behaviour:

- `events` table stores incoming mock productivity events
- `runs` table stores assistant run status and final output
- `chunks` table stores every streamed delta in order

## Estimated API cost

Mock mode costs ₹0 / US$0.

With `APP_USE_MOCK_LLM=false` and `gpt-4o-mini`, a typical classroom event uses a short prompt and short output. A full demo with 6–10 event runs should usually remain well below US$0.50, depending on current OpenAI pricing and output length.

## Troubleshooting

### `OPENAI_API_KEY not found`

The full demo does not require a key if mock mode is enabled.

Check `.env`:

```env
APP_USE_MOCK_LLM=true
```

For live OpenAI streaming, set:

```env
APP_USE_MOCK_LLM=false
OPENAI_API_KEY=sk-your-key-here
```

### Frontend says backend health check failed

Start the backend first:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Then refresh the dashboard.

### WebSocket connection failed

Check that:

- backend is running on port 8000
- frontend is running on port 5173
- `.env` has `FRONTEND_ORIGIN=http://localhost:5173`
- browser console does not show a blocked CORS/WebSocket request

### Port already in use

Use another port:

```bash
uvicorn backend.main:app --reload --port 8001
```

Then set frontend API base URL before starting Vite:

Windows PowerShell:

```bash
$env:VITE_API_BASE_URL="http://127.0.0.1:8001"
npm run dev
```

macOS/Linux:

```bash
VITE_API_BASE_URL=http://127.0.0.1:8001 npm run dev
```

### Reset the classroom demo

From the dashboard, click **Reset demo data**.

Or call:

```bash
curl -X POST http://127.0.0.1:8000/api/reset
```

## Further reading

- FastAPI WebSockets documentation: https://fastapi.tiangolo.com/advanced/websockets/
- FastAPI WebSocket testing documentation: https://fastapi.tiangolo.com/advanced/testing-websockets/
- OpenAI Python SDK: https://pypi.org/project/openai/
- OpenAI Responses API streaming reference: https://platform.openai.com/docs/api-reference/responses-streaming
- Vite getting started guide: https://vite.dev/guide/
- SQLite documentation: https://www.sqlite.org/docs.html
