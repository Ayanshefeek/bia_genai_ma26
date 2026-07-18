# Webhooks & FastAPI Triggers — Practical Package

Build a local FastAPI service that receives webhook-style HTTP events, validates JSON payloads, acknowledges quickly, and triggers a summarisation agent in the background.

This practical is designed for the **Webhooks & FastAPI Triggers** session in the **Real-Time & Event-Driven Agents** module. It prepares the backend trigger pattern used later in the streaming productivity assistant.

---

## Prerequisites

- Python 3.10 or 3.11
- VS Code or another editor
- Terminal access
- Optional: OpenAI API key
- No external GitHub, Gmail, or paid webhook provider setup is required

The package runs in **mock LLM mode by default**, so the full trigger flow works without an API key.

---

## Setup

### 1. Create a virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.sample .env
```

For a zero-cost classroom run, keep:

```env
USE_MOCK_LLM=true
```

For a real OpenAI call, set:

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
USE_MOCK_LLM=false
```

---

## How to run

### Option A — Run the API server

From the project root:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Open the interactive API docs:

```text
http://127.0.0.1:8000/docs
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

### Option B — Send a simulated support-form webhook

Keep the API server running in one terminal. In a second terminal:

```bash
python scripts/simulate_form_event.py
```

### Option C — Send a simulated GitHub issue webhook

```bash
python scripts/simulate_github_issue_event.py
```

### Option D — Run the notebook walkthrough

```bash
jupyter notebook notebook.ipynb
```

The notebook validates payloads, demonstrates webhook signing, starts a local API server, sends an event, polls the job, and shuts the server down.

---

## What each file does

```text
webhooks_fastapi_triggers/
├── notebook.ipynb                    # Guided classroom walkthrough
├── app/
│   ├── main.py                       # FastAPI app and webhook endpoints
│   ├── schemas.py                    # Pydantic request/response models
│   ├── agent.py                      # OpenAI/mock summarisation agent
│   ├── jobs.py                       # In-memory background job store
│   ├── security.py                   # HMAC webhook signature helpers
│   └── settings.py                   # Environment-based configuration
├── scripts/
│   ├── simulate_form_event.py        # Sends support-form webhook event
│   ├── simulate_github_issue_event.py# Sends GitHub issue webhook event
│   ├── demo_sequence.py              # Runs both simulations
│   └── send_raw_curl_examples.md     # cURL examples for HTTP-level teaching
├── data/
│   ├── form_event.json               # Sample support-form event
│   ├── github_issue_event.json       # Sample GitHub issue event
│   └── email_alert_event.json        # Extra event for exercises
├── tests/
│   └── test_schemas.py               # Lightweight validation tests
├── api_examples.http                 # VS Code REST Client examples
├── .env.sample                       # Environment variable template
├── requirements.txt                  # Pinned dependencies
├── README.md                         # Setup and usage guide
└── trainer_guide.md                  # Teaching flow and demo guidance
```

---

## Expected output

### Webhook acknowledgement

When you send a webhook, the API returns quickly:

```json
{
  "job_id": "job_123abc456def",
  "status": "queued",
  "message": "Event accepted. Agent processing started in the background."
}
```

### Job result after polling

```json
{
  "job_id": "job_123abc456def",
  "status": "completed",
  "event_id": "evt_form_1001",
  "event_type": "support.form_submitted",
  "source": "form",
  "result": {
    "summary": "I tried following the onboarding guide but the API key setup section is confusing.",
    "category": "setup_support",
    "priority": "medium",
    "recommended_action": "Review the event details, respond with the most relevant help, and log the outcome for follow-up."
  }
}
```

---

## Estimated API cost

Default classroom mode:

```text
USE_MOCK_LLM=true → ₹0 / $0
```

Real OpenAI mode:

```text
USE_MOCK_LLM=false with gpt-4o-mini
Estimated cost for this demo: typically far below $0.01 for the included short payloads.
```

Actual cost depends on model pricing, prompt length, response length, and provider pricing updates.

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'app'`

Run commands from the project root:

```bash
cd webhooks_fastapi_triggers
python -m uvicorn app.main:app --reload --port 8000
```

### `OPENAI_API_KEY is required when USE_MOCK_LLM=false`

Either set a valid key in `.env`, or switch back to:

```env
USE_MOCK_LLM=true
```

### `401 Invalid webhook signature`

For classroom simplicity, set:

```env
ACCEPT_UNSIGNED_EVENTS=true
```

Or use the provided simulation scripts, which sign events automatically.

### Port 8000 already in use

Use a different port:

```bash
python -m uvicorn app.main:app --reload --port 8001
```

Then set:

```env
SERVER_URL=http://127.0.0.1:8001
```

---

## Further reading

- FastAPI request bodies with Pydantic models: https://fastapi.tiangolo.com/tutorial/body/
- FastAPI background tasks: https://fastapi.tiangolo.com/tutorial/background-tasks/
- GitHub webhook events and payloads: https://docs.github.com/en/webhooks/webhook-events-and-payloads
- GitHub webhook delivery validation: https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries
- OpenAI model documentation: https://developers.openai.com/api/docs/models
