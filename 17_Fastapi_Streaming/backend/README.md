# Backend

FastAPI backend for the Streaming Productivity Assistant practical.

Run from the project root:

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Key endpoints:

- `GET /api/health`
- `GET /api/sample-events`
- `POST /api/trigger`
- `GET /api/runs`
- `WS /ws/runs/{run_id}`
