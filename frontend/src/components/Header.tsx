export function Header() {
  return (
    <header className="border-b border-gray-800 bg-black/80 backdrop-blur-sm" role="banner">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-center">
          <h1 className="text-3xl font-bold text-white" style={{ textShadow: '0 0 20px rgba(255, 255, 255, 0.6), 0 0 40px rgba(255, 255, 255, 0.4)' }}>
            cramCortex
          </h1>
        </div>
      </div>
    </header>
  )
}