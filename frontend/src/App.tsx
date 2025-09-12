import { Header } from "./components/Header"
import { HeroSection } from "./components/HeroSection"
import { UploadSection } from "./components/UploadSection"

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <HeroSection />
        <UploadSection />
      </main>
    </div>
  )
}

export default App
