const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export function audioUrl(path) {
  if (!path) return null
  if (path.startsWith('http')) return path
  return `${API_BASE}${path}`
}

export async function fetchPersonas() {
  const response = await fetch(`${API_BASE}/api/personas`)
  if (!response.ok) {
    throw new Error(`Could not load personas: ${response.status}`)
  }
  return response.json()
}

export async function sendChat({ message, personaId, includeAudio = true }) {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      persona_id: personaId,
      include_audio: includeAudio,
    }),
  })

  const payload = await response.json()
  if (!response.ok) {
    throw new Error(payload.detail || `Chat request failed: ${response.status}`)
  }
  return payload
}

export async function transcribeAudio(blob) {
  const formData = new FormData()
  formData.append('file', blob, 'classroom_recording.webm')

  const response = await fetch(`${API_BASE}/api/transcribe`, {
    method: 'POST',
    body: formData,
  })

  const payload = await response.json()
  if (!response.ok) {
    throw new Error(payload.detail || `Transcription failed: ${response.status}`)
  }
  return payload
}
