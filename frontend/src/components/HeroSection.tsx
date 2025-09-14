import { Zap, Target, BarChart3, BookOpen, Brain, Cpu } from 'lucide-react'
import { useState, useEffect } from 'react'

export function HeroSection() {
  return (
    <section className="text-center py-16 mb-12 relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute inset-0 bg-gradient-to-b from-blue-900/5 via-purple-900/5 to-blue-900/5 blur-3xl"></div>
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute top-1/2 right-1/4 w-48 h-48 bg-purple-500/10 rounded-full blur-3xl animate-pulse delay-1000"></div>

      <div className="relative z-10">
        <div className="mb-8 relative">
          {/* Erratic fast blinking circles */}
          <div className="absolute inset-0 pointer-events-none overflow-hidden">
            {/* Erratic blinking pattern */}
            <div className="absolute top-8 left-1/4 w-1.5 h-1.5 bg-white rounded-full animate-ping" style={{ animationDuration: '0.8s', boxShadow: '0 0 12px rgba(255,255,255,0.9)' }}></div>
            <div className="absolute top-12 right-1/3 w-1 h-1 bg-white rounded-full animate-ping" style={{ animationDelay: '0.2s', animationDuration: '1.1s', boxShadow: '0 0 8px rgba(255,255,255,0.7)' }}></div>
            <div className="absolute top-6 left-1/2 w-2 h-2 bg-white rounded-full animate-ping" style={{ animationDelay: '0.7s', animationDuration: '0.6s', boxShadow: '0 0 15px rgba(255,255,255,1)' }}></div>
            <div className="absolute left-8 top-1/3 w-1 h-1 bg-white rounded-full animate-ping" style={{ animationDelay: '0.1s', animationDuration: '1.3s', boxShadow: '0 0 8px rgba(255,255,255,0.6)' }}></div>
            <div className="absolute right-12 top-1/2 w-1.5 h-1.5 bg-white rounded-full animate-ping" style={{ animationDelay: '0.4s', animationDuration: '0.9s', boxShadow: '0 0 12px rgba(255,255,255,0.8)' }}></div>
            <div className="absolute right-6 top-1/4 w-1 h-1 bg-white rounded-full animate-ping" style={{ animationDelay: '0.8s', animationDuration: '0.7s', boxShadow: '0 0 8px rgba(255,255,255,0.7)' }}></div>
            <div className="absolute bottom-8 left-1/3 w-1.5 h-1.5 bg-white rounded-full animate-ping" style={{ animationDelay: '0.3s', animationDuration: '1.2s', boxShadow: '0 0 12px rgba(255,255,255,0.8)' }}></div>
            <div className="absolute bottom-12 right-1/4 w-1 h-1 bg-white rounded-full animate-ping" style={{ animationDelay: '0.6s', animationDuration: '0.5s', boxShadow: '0 0 8px rgba(255,255,255,0.9)' }}></div>
            <div className="absolute bottom-6 right-1/2 w-2 h-2 bg-white rounded-full animate-ping" style={{ animationDelay: '0.9s', animationDuration: '1.0s', boxShadow: '0 0 15px rgba(255,255,255,0.8)' }}></div>
          </div>

          <h2 className="relative text-5xl md:text-7xl font-bold text-white mb-6 leading-tight"
              style={{
                textShadow: '0 0 40px rgba(255, 255, 255, 0.9), 0 0 80px rgba(255, 255, 255, 0.4), 0 0 120px rgba(59, 130, 246, 0.3)',
                letterSpacing: '-0.02em'
              }}>
            Transform Your
            <br />
            Test Preparation
          </h2>

          <div className="relative inline-block">
            <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-4xl mx-auto leading-relaxed"
               style={{ textShadow: '0 0 15px rgba(255, 255, 255, 0.4)' }}>
              Transform passive test review into
              <span className="text-white font-semibold"> active, structured preparation </span>
              through AI-powered analysis.
            </p>
          </div>
        </div>

        {/* Premium feature highlights - elegant and minimal */}
        <div className="flex flex-wrap justify-center gap-8 text-sm text-gray-400 mb-12 max-w-4xl mx-auto">
          <div className="flex items-center group">
            <div className="w-2 h-2 bg-white/60 rounded-full mr-3 shadow-[0_0_15px_rgba(255,255,255,0.8)] group-hover:shadow-[0_0_25px_rgba(255,255,255,1)] transition-all duration-300"></div>
            <span className="text-gray-300 group-hover:text-white transition-colors" style={{ textShadow: '0 0 10px rgba(255, 255, 255, 0.3)' }}>
              Question Classification
            </span>
          </div>
          <div className="flex items-center group">
            <div className="w-2 h-2 bg-white/60 rounded-full mr-3 shadow-[0_0_15px_rgba(255,255,255,0.8)] group-hover:shadow-[0_0_25px_rgba(255,255,255,1)] transition-all duration-300"></div>
            <span className="text-gray-300 group-hover:text-white transition-colors" style={{ textShadow: '0 0 10px rgba(255, 255, 255, 0.3)' }}>
              Topic Clustering
            </span>
          </div>
          <div className="flex items-center group">
            <div className="w-2 h-2 bg-white/60 rounded-full mr-3 shadow-[0_0_15px_rgba(255,255,255,0.8)] group-hover:shadow-[0_0_25px_rgba(255,255,255,1)] transition-all duration-300"></div>
            <span className="text-gray-300 group-hover:text-white transition-colors" style={{ textShadow: '0 0 10px rgba(255, 255, 255, 0.3)' }}>
              Smart Analytics
            </span>
          </div>
          <div className="flex items-center group">
            <div className="w-2 h-2 bg-white/60 rounded-full mr-3 shadow-[0_0_15px_rgba(255,255,255,0.8)] group-hover:shadow-[0_0_25px_rgba(255,255,255,1)] transition-all duration-300"></div>
            <span className="text-gray-300 group-hover:text-white transition-colors" style={{ textShadow: '0 0 10px rgba(255, 255, 255, 0.3)' }}>
              Instant Processing
            </span>
          </div>
        </div>

        {/* Call to action hint */}
        <div className="animate-bounce">
          <p className="text-gray-400 text-sm"
             style={{ textShadow: '0 0 10px rgba(255, 255, 255, 0.3)' }}>
            Upload your test PDFs below to get started
          </p>
        </div>
      </div>
    </section>
  )
}