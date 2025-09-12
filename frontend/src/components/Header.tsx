export function Header() {
  return (
    <header className="border-b bg-white/80 backdrop-blur-sm" role="banner">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div 
              className="flex items-center justify-center w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg"
              aria-label="cramCortex logo"
            >
              <span className="text-white font-bold text-lg" aria-hidden="true">C</span>
            </div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              cramCortex
            </h1>
          </div>
          <nav className="hidden md:flex items-center space-x-6" role="navigation" aria-label="Main navigation">
            <a 
              href="#" 
              className="text-gray-600 hover:text-gray-900 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md px-2 py-1"
            >
              Features
            </a>
            <a 
              href="#" 
              className="text-gray-600 hover:text-gray-900 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md px-2 py-1"
            >
              Pricing
            </a>
            <a 
              href="#" 
              className="text-gray-600 hover:text-gray-900 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md px-2 py-1"
            >
              About
            </a>
          </nav>
        </div>
      </div>
    </header>
  )
}