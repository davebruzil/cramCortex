import { Brain, Sparkles } from 'lucide-react'
import { useState } from 'react'

export function Header() {
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 })

  const handleMouseMove = (e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect()
    setMousePos({
      x: ((e.clientX - rect.left) / rect.width - 0.5) * 20,
      y: ((e.clientY - rect.top) / rect.height - 0.5) * 10
    })
  }

  return (
    <header
      className="border-b border-gray-800/50 bg-gradient-to-r from-black/90 via-gray-900/90 to-black/90 backdrop-blur-md shadow-2xl relative overflow-hidden"
      role="banner"
      onMouseMove={handleMouseMove}
    >
      {/* Neural network background particles */}
      <div className="absolute inset-0 pointer-events-none">
        {[...Array(15)].map((_, i) => (
          <div
            key={i}
            className="absolute w-px h-px bg-white/30 rounded-full animate-ping"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${i * 0.4}s`,
              animationDuration: '4s'
            }}
          />
        ))}
      </div>

      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-center relative">
          {/* Magnetic field effect */}
          <div className="absolute inset-0 bg-gradient-to-r from-white/3 via-white/8 to-white/3 blur-3xl animate-pulse"></div>

          <div
            className="flex items-center space-x-3 relative z-10 transition-transform duration-300 ease-out"
            style={{
              transform: `translateX(${mousePos.x}px) translateY(${mousePos.y}px)`
            }}
          >
            {/* Orbital logo with floating particles */}
            <div className="relative group">
              {/* Floating particles around brain */}
              {[...Array(4)].map((_, i) => (
                <div
                  key={i}
                  className="absolute w-1 h-1 bg-white/60 rounded-full"
                  style={{
                    left: `${Math.cos(i * Math.PI / 2) * 25 + 16}px`,
                    top: `${Math.sin(i * Math.PI / 2) * 25 + 16}px`,
                    animation: `float 3s ease-in-out infinite`,
                    animationDelay: `${i * 0.7}s`
                  }}
                />
              ))}

              <Brain
                className="h-8 w-8 text-white group-hover:animate-spin transition-all duration-1000"
                style={{
                  filter: 'drop-shadow(0 0 20px rgba(255, 255, 255, 0.9))'
                }}
              />
            </div>

            {/* Brand name with synaptic effect */}
            <h1
              className="text-4xl font-bold text-white relative group cursor-default"
              style={{
                textShadow: '0 0 30px rgba(255, 255, 255, 0.8), 0 0 60px rgba(255, 255, 255, 0.6)',
                fontFamily: 'system-ui, -apple-system, sans-serif',
                letterSpacing: '-0.02em'
              }}
            >
              cramCortex
            </h1>
          </div>
        </div>
      </div>
    </header>
  )
}