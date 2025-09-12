export function HeroSection() {
  return (
    <section className="text-center py-12 mb-8">
      <h2 className="text-4xl md:text-5xl font-bold text-white mb-4" style={{ textShadow: '0 0 30px rgba(255, 255, 255, 0.8), 0 0 60px rgba(255, 255, 255, 0.4)' }}>
        Transform Your Test Preparation
      </h2>
      <p className="text-xl text-gray-300 mb-6 max-w-3xl mx-auto" style={{ textShadow: '0 0 15px rgba(255, 255, 255, 0.3)' }}>
        Transform passive test review into active, structured preparation through AI-powered test analysis and intelligent study modes.
      </p>
      <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-400 mb-8">
        <div className="flex items-center">
          <div className="w-2 h-2 bg-green-400 rounded-full mr-2 shadow-[0_0_10px_rgba(74,222,128,0.8)]"></div>
          <span style={{ textShadow: '0 0 10px rgba(255, 255, 255, 0.3)' }}>Question Classification</span>
        </div>
        <div className="flex items-center">
          <div className="w-2 h-2 bg-blue-400 rounded-full mr-2 shadow-[0_0_10px_rgba(96,165,250,0.8)]"></div>
          <span style={{ textShadow: '0 0 10px rgba(255, 255, 255, 0.3)' }}>Topic Clustering</span>  
        </div>
        <div className="flex items-center">
          <div className="w-2 h-2 bg-purple-400 rounded-full mr-2 shadow-[0_0_10px_rgba(196,181,253,0.8)]"></div>
          <span style={{ textShadow: '0 0 10px rgba(255, 255, 255, 0.3)' }}>Smart Analytics</span>
        </div>
      </div>
    </section>
  )
}