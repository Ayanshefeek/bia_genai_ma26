# Avatar Persona Agent

A comprehensive practical build for a browser-based 3-D avatar persona agent: persona-controlled LLM response, text-to-speech audio, optional browser voice recording, and a React + Three.js talking head.

## Prerequisites

- Python 3.10 or 3.11
- Node.js 20+ and npm
- A modern browser with microphone permission support
- OpenAI API key for real LLM, speech-to-text, and text-to-speech calls
- VS Code or another editor with Python and JavaScript support

The project also runs in `MOCK_MODE=true` without an API key, which is useful for classroom setup checks.

## Setup

### 1. Create a Python environment

From the project root:

```bash
python -m venv .venv
```

Activate it:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Install backend requirements:

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy the template:

```bash
# Windows PowerShell
copy .env.sample .env

# macOS/Linux
cp .env.sample .env
```

Edit `.env` and add your API key:

```bash
OPENAI_API_KEY=sk-your-key-here
```

For a no-cost dry run:

```bash
MOCK_MODE=true
```

### 3. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

## How to run

### Start the backend

From the project root:

```bash
uvicorn backend.app:app --reload --port 8000
```

Check the backend:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok","mock_mode":false}
```

### Start the frontend

In a second terminal:

```bash
cd frontend
npm run dev
```

Open:

```text
http://127.0.0.1:5173
```

Type a message, choose a persona, and click **Ask avatar**. The avatar should move from thinking to speaking and back to idle.

## What each file does

```text
avatar_persona_agent/
├── backend/
│   ├── app.py                # FastAPI routes for chat, transcription, audio serving, health
│   ├── agent_service.py      # Persona-controlled LLM generation
│   ├── audio_service.py      # TTS and STT helpers
│   ├── avatar_cues.py        # Animation-state cues sent to the frontend
│   ├── config.py             # Environment-variable loading
│   ├── persona.py            # Persona cards and prompt construction
│   ├── schemas.py            # Pydantic request/response schemas
│   └── utils.py              # Timing, filenames, mock WAV generation
├── frontend/
│   ├── src/App.jsx           # Main classroom UI
│   ├── src/components/       # Avatar canvas, procedural avatar, recorder
│   ├── src/hooks/            # Web Audio amplitude hook
│   ├── src/services/api.js   # Fetch calls to backend
│   └── src/styles.css        # BIA-blue visual styling
├── data/persona_cards.json   # Human-readable persona examples
├── notebook.ipynb            # Guided notebook for practical teaching
├── .env.sample               # Environment variable template
├── requirements.txt          # Pinned Python dependencies
├── trainer_guide.md          # Detailed classroom delivery guide
└── README.md                 # This file
```

## Expected output

By the end of the practical, the running app should demonstrate this flow:

```text
Typed or recorded user input
→ FastAPI backend
→ persona prompt + LLM response
→ TTS audio file
→ browser audio playback
→ live mouth movement from audio amplitude
→ avatar returns to idle
```

In mock mode, the same flow works with deterministic mock text and synthetic WAV audio.

## Estimated API cost

A short classroom run with 5–8 turns is usually low-cost because the prompts are short and responses are intentionally brief.

Approximate cost factors:

- LLM response: depends on selected text model and token count.
- TTS: depends on selected TTS model and response length.
- STT: depends on uploaded audio duration.

Keep each recorded clip under 10 seconds and each avatar answer under 7 spoken sentences. Target practical cost: **well under ₹50 / under $0.50** for a short demo, depending on the chosen models and current provider pricing.

## Troubleshooting

### Backend starts in mock mode even after adding an API key

Check that `.env` is in the project root, not inside `backend/`. Restart Uvicorn after editing `.env`.

### Browser says microphone access failed

Use typed input first. Then check browser permissions, HTTPS restrictions, and whether another app is already using the microphone.

### Frontend cannot reach backend

Confirm backend is running on `http://127.0.0.1:8000`. Check that `.env` has:

```bash
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Audio plays but mouth does not move

The browser may block audio analysis until the user interacts with the page. Click **Ask avatar** again after the first interaction. Also check that the browser tab is not muted.

### TTS fails but text generation works

Verify `OPENAI_TTS_MODEL` and `OPENAI_TTS_VOICE` in `.env`. Switch to mock mode to continue teaching while debugging the TTS setting.

## Further reading

- OpenAI audio and speech docs: https://developers.openai.com/api/docs/guides/audio
- OpenAI speech-to-text docs: https://developers.openai.com/api/docs/guides/speech-to-text
- FastAPI CORS docs: https://fastapi.tiangolo.com/tutorial/cors/
- React Three Fiber docs: https://r3f.docs.pmnd.rs/getting-started/installation
- Three.js loading 3D models: https://threejs.org/manual/en/loading-3d-models.html

## Classroom extension ideas

- Replace the procedural avatar with a GLB model.
- Add viseme timestamps instead of amplitude-based mouth movement.
- Stream partial text to the frontend before TTS finishes.
- Add conversation memory with a short rolling transcript.
- Add a safety layer that blocks persona-inconsistent responses.
