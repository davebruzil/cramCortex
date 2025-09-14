import { Header } from "../components/Header"
import { HeroSection } from "../components/HeroSection"
import { UploadSection } from "../components/UploadSection"

export function Home() {
  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Enhanced multi-layer background */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-900 via-black to-gray-800"></div>

      {/* Subtle animated background elements - monochrome */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-white/3 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 right-1/4 w-80 h-80 bg-white/2 rounded-full blur-3xl animate-pulse delay-2000"></div>
        <div className="absolute bottom-1/4 left-1/2 w-64 h-64 bg-white/3 rounded-full blur-3xl animate-pulse delay-3000"></div>

        {/* Subtle grid pattern */}
        <div className="absolute inset-0 opacity-[0.02]" style={{
          backgroundImage: `radial-gradient(circle at 1px 1px, rgba(255,255,255,0.15) 1px, transparent 0)`,
          backgroundSize: '50px 50px'
        }}></div>
      </div>

      <div className="relative z-10">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <HeroSection />
          <UploadSection />
        </main>
      </div>

      {/* Bottom fade effect */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-black/50 to-transparent pointer-events-none"></div>
    </div>
  )
}