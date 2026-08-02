import { useEffect, useState } from 'react'
import AvatarCanvas from './components/AvatarCanvas.jsx'
import VoiceRecorder from './components/VoiceRecorder.jsx'
import { useAudioAvatar } from './hooks/useAudioAvatar.js'
import { fetchPersonas, sendChat, transcribeAudio } from './services/api.js'

const samplePrompts = [
  'Explain the avatar agent pipeline in plain language.',
  'Give me three ways to reduce latency in this system.',
  'Act as a support concierge and help me troubleshoot a login issue.',
]

export default function App() {
  const [personas, setPersonas] = useState([])
  const [personaId, setPersonaId] = useState('bia_ai_mentor')
  const [message, setMessage] = useState(samplePrompts[0])
  const [assistantText, setAssistantText] = useState('')
  const [latencyMs, setLatencyMs] = useState(null)
  const [costNote, setCostNote] = useState('')
  const [avatarState, setAvatarState] = useState('idle')
  const [isBusy, setIsBusy] = useState(false)
  const [error, setError] = useState('')
  const { amplitude, isPlaying, playAudio, stopAudio } = useAudioAvatar()

  useEffect(() => {
    fetchPersonas()
      .then((items) => {
        setPersonas(items)
        if (items.length > 0) setPersonaId(items[0].persona_id)
      })
      .catch((err) => setError(err.message))
  }, [])

  async function handleSubmit(event) {
    event.preventDefault()
    if (!message.trim()) return

    setError('')
    setIsBusy(true)
    setAvatarState('thinking')
    stopAudio()

    try {
      const response = await sendChat({
        message: message.trim(),
        personaId,
        includeAudio: true,
      })

      setAssistantText(response.assistant_text)
      setLatencyMs(response.latency_ms)
      setCostNote(response.cost_note)

      if (response.audio_url) {
        setAvatarState('speaking')
        await playAudio(response.audio_url, () => setAvatarState('idle'))
      } else {
        setAvatarState('idle')
      }
    } catch (err) {
      setAvatarState('error')
      setError(err.message)
    } finally {
      setIsBusy(false)
    }
  }

  async function handleAudioReady(blob) {
    setError('')
    setIsBusy(true)
    setAvatarState('listening')

    try {
      const response = await transcribeAudio(blob)
      setMessage(response.text)
      setCostNote(response.cost_note)
      setAvatarState('idle')
    } catch (err) {
      setAvatarState('error')
      setError(err.message)
    } finally {
      setIsBusy(false)
    }
  }

  function loadSamplePrompt(index) {
    setMessage(samplePrompts[index])
  }

  return (
    <main className="app-shell">
      <section className="left-panel">
        <div className="eyebrow">BIA practical build</div>
        <h1>3-D Avatar & Persona Agent</h1>
        <p className="subtitle">
          Connect a persona-controlled agent to speech output and a browser-rendered talking head.
        </p>

        <form onSubmit={handleSubmit} className="control-card">
          <label htmlFor="persona">Persona</label>
          <select
            id="persona"
            value={personaId}
            onChange={(event) => setPersonaId(event.target.value)}
            disabled={isBusy}
          >
            {personas.map((persona) => (
              <option key={persona.persona_id} value={persona.persona_id}>
                {persona.name} — {persona.role}
              </option>
            ))}
          </select>

          <label htmlFor="message">User message</label>
          <textarea
            id="message"
            rows="5"
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            disabled={isBusy}
          />

          <div className="sample-row">
            {samplePrompts.map((_, index) => (
              <button key={index} type="button" className="chip" onClick={() => loadSamplePrompt(index)}>
                Prompt {index + 1}
              </button>
            ))}
          </div>

          <VoiceRecorder onAudioReady={handleAudioReady} disabled={isBusy} />

          <button type="submit" disabled={isBusy || !message.trim()}>
            {isBusy ? 'Working...' : 'Ask avatar'}
          </button>
        </form>

        {error && <div className="error-box">{error}</div>}

        <div className="response-card">
          <h2>Assistant response</h2>
          <p>{assistantText || 'The response will appear here after the first turn.'}</p>
          <div className="meta-row">
            <span>Latency: {latencyMs ? `${latencyMs} ms` : '—'}</span>
            <span>{isPlaying ? 'Audio playing' : 'Audio idle'}</span>
          </div>
          <small>{costNote}</small>
        </div>
      </section>

      <section className="right-panel">
        <AvatarCanvas state={avatarState} amplitude={amplitude} />
        <div className="teaching-note">
          <strong>What to observe:</strong> The avatar state changes before, during, and after audio playback.
          The mouth movement is driven by live audio amplitude, a classroom-friendly approximation of viseme-based lip sync.
        </div>
      </section>
    </main>
  )
}
