# Practical Lesson Plan — Avatar Persona Agent

## Learning outcomes

After completing the practical, participants can:

1. Explain the difference between a voice bot and an avatar persona agent.
2. Build a FastAPI backend that hides provider API keys.
3. Design persona prompts that are suitable for spoken output.
4. Return frontend-friendly avatar cues from an agent backend.
5. Connect React UI state to a Three.js avatar.
6. Use browser audio amplitude to approximate mouth movement.
7. Identify latency bottlenecks in STT → LLM → TTS → avatar systems.

## Practical milestones

### Milestone A — Run the system in mock mode

Goal: prove that the local backend/frontend connection works before using paid APIs.

```bash
MOCK_MODE=true
uvicorn backend.app:app --reload --port 8000
cd frontend
npm run dev
```

Success signal: typed input produces mock text and synthetic audio.

### Milestone B — Run a real LLM + TTS turn

Goal: switch from mock response to provider-backed response.

Success signal: the assistant response changes according to selected persona and audio is generated.

### Milestone C — Test voice input

Goal: record a short browser clip, transcribe it, and reuse the transcript as the next user message.

Success signal: transcript appears in the text area.

### Milestone D — Customize persona

Goal: modify `backend/persona.py`.

Success signal: new persona appears in the dropdown and changes response style.

### Milestone E — Modify avatar behavior

Goal: change mouth or state behavior in `ProceduralAvatar.jsx`.

Success signal: visible animation change during speaking/thinking.

## Assessment checklist

- Backend starts with no stack trace.
- Frontend loads at the Vite URL.
- `/health` returns status `ok`.
- `/api/personas` returns at least three personas.
- `/api/chat` returns text, audio URL, latency, and avatar cues.
- Avatar state changes from thinking to speaking to idle.
- API keys are not present in frontend code.
- Persona instructions produce short, spoken-style answers.
