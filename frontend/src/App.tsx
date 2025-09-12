import { Header } from "./components/Header"
import { HeroSection } from "./components/HeroSection"
import { UploadSection } from "./components/UploadSection"

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-800">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <HeroSection />
        <UploadSection />
      </main>
    </div>
  )
}

export default App
