export function HeroSection() {
  return (
    <section className="text-center py-12 mb-8">
      <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
        Transform Your Test Preparation
      </h2>
      <p className="text-xl text-gray-600 mb-6 max-w-3xl mx-auto">
        Transform passive test review into active, structured preparation through AI-powered test analysis and intelligent study modes.
      </p>
      <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-500 mb-8">
        <div className="flex items-center">
          <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
          Question Classification
        </div>
        <div className="flex items-center">
          <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
          Topic Clustering  
        </div>
        <div className="flex items-center">
          <div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
          Smart Analytics
        </div>
      </div>
    </section>
  )
}