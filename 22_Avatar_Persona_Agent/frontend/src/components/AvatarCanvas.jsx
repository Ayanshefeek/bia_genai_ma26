import { Canvas } from '@react-three/fiber'
import ProceduralAvatar from './ProceduralAvatar.jsx'

export default function AvatarCanvas({ state, amplitude }) {
  return (
    <div className="avatar-card">
      <Canvas camera={{ position: [0, 0.15, 4], fov: 45 }}>
        <ambientLight intensity={1.8} />
        <directionalLight position={[3, 4, 5]} intensity={2.2} />
        <pointLight position={[-3, -2, 4]} intensity={0.9} />
        <ProceduralAvatar state={state} amplitude={amplitude} />
      </Canvas>
      <div className={`avatar-status state-${state}`}>
        {state.toUpperCase()}
      </div>
    </div>
  )
}
