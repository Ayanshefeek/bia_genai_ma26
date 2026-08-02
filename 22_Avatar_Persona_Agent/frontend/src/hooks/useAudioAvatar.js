import { useCallback, useRef, useState } from 'react'
import { audioUrl } from '../services/api.js'

export function useAudioAvatar() {
  const [amplitude, setAmplitude] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const audioRef = useRef(null)
  const animationFrameRef = useRef(null)

  const stopAudio = useCallback(() => {
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
      animationFrameRef.current = null
    }

    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }

    setAmplitude(0)
    setIsPlaying(false)
  }, [])

  const playAudio = useCallback(async (path, onEnded) => {
    stopAudio()

    const finalUrl = audioUrl(path)
    if (!finalUrl) {
      setIsPlaying(false)
      return
    }

    const audio = new Audio(finalUrl)
    audio.crossOrigin = 'anonymous'
    audioRef.current = audio

    const AudioContextClass = window.AudioContext || window.webkitAudioContext
    const audioContext = new AudioContextClass()
    const source = audioContext.createMediaElementSource(audio)
    const analyser = audioContext.createAnalyser()
    analyser.fftSize = 256
    source.connect(analyser)
    analyser.connect(audioContext.destination)

    const dataArray = new Uint8Array(analyser.frequencyBinCount)

    const tick = () => {
      analyser.getByteFrequencyData(dataArray)
      const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length
      setAmplitude(Math.min(1, average / 95))
      animationFrameRef.current = requestAnimationFrame(tick)
    }

    audio.onended = () => {
      stopAudio()
      if (onEnded) onEnded()
    }

    setIsPlaying(true)
    await audio.play()
    tick()
  }, [stopAudio])

  return {
    amplitude,
    isPlaying,
    playAudio,
    stopAudio,
  }
}
