# Raw cURL Examples

Use these commands when you want to show the HTTP layer without Python helper scripts.

## Health check

```bash
curl http://127.0.0.1:8000/health
```

## Unsigned text-submitted webhook

This works only when `ACCEPT_UNSIGNED_EVENTS=true` in `.env`.

```bash
curl -X POST http://127.0.0.1:8000/webhooks/text-submitted \
  -H "Content-Type: application/json" \
  -d @data/form_event.json
```

## Get all jobs

```bash
curl http://127.0.0.1:8000/jobs
```

## Reset in-memory jobs

```bash
curl -X POST http://127.0.0.1:8000/admin/reset-jobs
```
