import { useRef, useState } from 'react'

export default function VoiceRecorder({ onAudioReady, disabled }) {
  const [isRecording, setIsRecording] = useState(false)
  const recorderRef = useRef(null)
  const chunksRef = useRef([])

  async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
    recorderRef.current = recorder
    chunksRef.current = []

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunksRef.current.push(event.data)
    }

    recorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
      stream.getTracks().forEach((track) => track.stop())
      onAudioReady(blob)
    }

    recorder.start()
    setIsRecording(true)
  }

  function stopRecording() {
    if (recorderRef.current && recorderRef.current.state !== 'inactive') {
      recorderRef.current.stop()
    }
    setIsRecording(false)
  }

  return (
    <div className="recorder-row">
      {!isRecording ? (
        <button type="button" onClick={startRecording} disabled={disabled}>
          Record voice
        </button>
      ) : (
        <button type="button" onClick={stopRecording} className="secondary">
          Stop recording
        </button>
      )}
      <span className="recorder-hint">
        Voice is optional. Typed input is the reliable classroom fallback.
      </span>
    </div>
  )
}
