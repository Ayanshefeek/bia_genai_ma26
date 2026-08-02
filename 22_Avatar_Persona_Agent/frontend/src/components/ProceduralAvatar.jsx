import { useFrame } from '@react-three/fiber'
import { useRef } from 'react'

function statusColor(state) {
  if (state === 'listening') return '#5B9BD5'
  if (state === 'thinking') return '#4472C4'
  if (state === 'speaking') return '#161A3E'
  if (state === 'error') return '#C0392B'
  return '#D6E4F0'
}

export default function ProceduralAvatar({ state, amplitude }) {
  const headRef = useRef()
  const mouthRef = useRef()
  const ringRef = useRef()

  useFrame((clockState) => {
    const time = clockState.clock.getElapsedTime()
    if (headRef.current) {
      headRef.current.rotation.y = Math.sin(time * 0.7) * 0.08
      headRef.current.position.y = Math.sin(time * 1.2) * 0.025
    }

    if (mouthRef.current) {
      const idleMouth = state === 'speaking' ? 0.08 : 0.015
      const mouthOpen = state === 'speaking' ? idleMouth + amplitude * 0.35 : idleMouth
      mouthRef.current.scale.y = Math.max(0.08, mouthOpen)
      mouthRef.current.position.y = -0.22 - mouthOpen * 0.12
    }

    if (ringRef.current) {
      ringRef.current.rotation.z = time * 0.8
      ringRef.current.scale.setScalar(state === 'thinking' ? 1 + Math.sin(time * 5) * 0.06 : 1)
      ringRef.current.visible = state === 'thinking'
    }
  })

  return (
    <group ref={headRef} position={[0, 0, 0]}>
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[1, 64, 64]} />
        <meshStandardMaterial color="#D6E4F0" roughness={0.55} metalness={0.05} />
      </mesh>

      <mesh position={[-0.34, 0.24, 0.86]}>
        <sphereGeometry args={[0.09, 24, 24]} />
        <meshStandardMaterial color="#161A3E" />
      </mesh>

      <mesh position={[0.34, 0.24, 0.86]}>
        <sphereGeometry args={[0.09, 24, 24]} />
        <meshStandardMaterial color="#161A3E" />
      </mesh>

      <mesh ref={mouthRef} position={[0, -0.34, 0.92]}>
        <boxGeometry args={[0.48, 0.22, 0.04]} />
        <meshStandardMaterial color="#161A3E" />
      </mesh>

      <mesh position={[0, -1.16, 0]}>
        <cylinderGeometry args={[0.72, 0.95, 0.95, 48]} />
        <meshStandardMaterial color={statusColor(state)} roughness={0.6} />
      </mesh>

      <mesh ref={ringRef} position={[0, 0.03, 1.04]}>
        <torusGeometry args={[1.13, 0.018, 16, 96]} />
        <meshStandardMaterial color="#4472C4" emissive="#4472C4" emissiveIntensity={0.4} />
      </mesh>
    </group>
  )
}
