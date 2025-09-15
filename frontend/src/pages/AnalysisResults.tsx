import { useLocation, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { ArrowLeft, Upload, FileText, BarChart3, Target, Brain, PieChart, ArrowRight } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import type { AnalysisResult } from '../types/analysis'

export function AnalysisResults() {
  const location = useLocation()
  const navigate = useNavigate()
  const [analysisData, setAnalysisData] = useState<AnalysisResult | null>(null)

  useEffect(() => {
    // Get analysis data passed from the previous page
    if (location.state?.analysisData) {
      setAnalysisData(location.state.analysisData)
    } else {
      // If no data, redirect back to upload
      navigate('/')
    }
  }, [location.state, navigate])

  const handleBackToUpload = () => {
    navigate('/')
  }

  const handleNewUpload = () => {
    navigate('/')
  }

  const handlePracticeQuestionType = (questionType: string) => {
    // Navigate to practice view with the question type and analysis data
    navigate(`/practice/${questionType}`, { 
      state: { 
        analysisData,
        questionType 
      } 
    })
  }

  if (!analysisData) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white" style={{ textShadow: '0 0 10px rgba(255, 255, 255, 0.5)' }}>
            Loading analysis results...
          </p>
        </div>
      </div>
    )
  }

  const getQuestionTypeStats = () => {
    const stats = analysisData.analysis_data.questions.reduce((acc, q) => {
      acc[q.question_type] = (acc[q.question_type] || 0) + 1
      return acc
    }, {} as Record<string, number>)
    
    return Object.entries(stats).map(([type, count]) => ({
      type,
      count,
      percentage: Math.round((count / analysisData.analysis_data.questions.length) * 100)
    }))
  }

  const getQuestionTypeIcon = (type: string) => {
    switch (type) {
      case 'multiple_choice':
        return <Target className="h-5 w-5" />
      case 'true_false':
        return <BarChart3 className="h-5 w-5" />
      case 'short_answer':
        return <FileText className="h-5 w-5" />
      case 'essay':
        return <Brain className="h-5 w-5" />
      default:
        return <FileText className="h-5 w-5" />
    }
  }

  const getQuestionTypeColor = (type: string) => {
    switch (type) {
      case 'multiple_choice':
        return 'from-blue-900/30 to-blue-800/30 border-blue-600'
      case 'true_false':
        return 'from-green-900/30 to-green-800/30 border-green-600'
      case 'short_answer':
        return 'from-purple-900/30 to-purple-800/30 border-purple-600'
      case 'essay':
        return 'from-orange-900/30 to-orange-800/30 border-orange-600'
      default:
        return 'from-gray-900/30 to-gray-800/30 border-gray-600'
    }
  }

  const formatQuestionType = (type: string) => {
    return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  const questionTypeStats = getQuestionTypeStats()

  return (
    <div className="min-h-screen bg-black">
      {/* Enhanced Header & Hero Section */}
      <div className="relative overflow-hidden border-b border-gray-800 bg-gradient-to-br from-gray-900 via-black to-gray-900">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.03),transparent_70%)]" />
        <div className="max-w-7xl mx-auto px-4 py-12 relative">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleBackToUpload}
                className="text-gray-400 hover:text-white hover:bg-gray-800/50 backdrop-blur-sm"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Upload
              </Button>
              <div>
                <h1 className="text-3xl font-bold text-white" style={{ textShadow: '0 0 20px rgba(255, 255, 255, 0.6)' }}>
                  Analysis Complete
                </h1>
                <p className="text-gray-300 mt-1">
                  {analysisData.filename || 'Document'} • Ready for practice
                </p>
              </div>
            </div>
            <Button
              onClick={handleNewUpload}
              className="bg-white/10 text-white border border-white/20 backdrop-blur-sm hover:bg-white hover:text-black transition-all duration-300"
            >
              <Upload className="h-4 w-4 mr-2" />
              Analyze Another File
            </Button>
          </div>

          {/* Quick insights banner */}
          <div className="grid grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-4xl font-bold text-white mb-2" style={{ textShadow: '0 0 20px rgba(255, 255, 255, 0.6)' }}>
                {analysisData.analysis_data.summary.total_questions}
              </div>
              <div className="text-gray-400 text-sm">Total Questions</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-400 mb-2" style={{ textShadow: '0 0 20px rgba(59, 130, 246, 0.6)' }}>
                {questionTypeStats.length}
              </div>
              <div className="text-gray-400 text-sm">Question Types</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-purple-400 mb-2" style={{ textShadow: '0 0 20px rgba(147, 51, 234, 0.6)' }}>
                {analysisData.analysis_data.topics.length}
              </div>
              <div className="text-gray-400 text-sm">Topics Covered</div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-12 gap-8 min-h-[70vh]">

          {/* LEFT COLUMN: Question Types (60% width) */}
          <div className="col-span-12 lg:col-span-7 xl:col-span-8">
            <div className="sticky top-8">
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-2xl font-bold text-white" style={{ textShadow: '0 0 15px rgba(255, 255, 255, 0.5)' }}>
                  Practice Question Types
                </h2>
                <PieChart className="h-6 w-6 text-gray-400" />
              </div>

              {/* Enhanced horizontal card layout */}
              <div className="space-y-4">
                {questionTypeStats.map(({ type, count, percentage }, index) => (
                  <Card
                    key={type}
                    className={`cursor-pointer group transition-all duration-300 hover:scale-[1.01] bg-gradient-to-r ${getQuestionTypeColor(type)} border-l-4 hover:shadow-[0_0_30px_rgba(255,255,255,0.1)] ${
                      index === 0 ? 'h-32' : index === 1 ? 'h-28' : 'h-24'
                    }`}
                    onClick={() => handlePracticeQuestionType(type)}
                  >
                    <CardContent className="p-6 h-full">
                      <div className="flex items-center justify-between h-full">

                        {/* LEFT: Icon + Title */}
                        <div className="flex items-center space-x-4">
                          <div className="p-3 rounded-full bg-white/10 backdrop-blur-sm">
                            {getQuestionTypeIcon(type)}
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-white mb-1">
                              {formatQuestionType(type)}
                            </h3>
                            <p className="text-gray-300 text-sm">{count} questions available</p>
                          </div>
                        </div>

                        {/* CENTER: Progress Visual */}
                        <div className="flex flex-col items-center space-y-2">
                          <div className="relative w-16 h-16">
                            <svg className="w-16 h-16 transform -rotate-90" viewBox="0 0 36 36">
                              <path
                                d="m18,2.0845 a 15.9155,15.9155 0 0,1 0,31.831 a 15.9155,15.9155 0 0,1 0,-31.831"
                                fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="2"
                              />
                              <path
                                d="m18,2.0845 a 15.9155,15.9155 0 0,1 0,31.831 a 15.9155,15.9155 0 0,1 0,-31.831"
                                fill="none" stroke="white" strokeWidth="2"
                                strokeDasharray={`${percentage}, 100`}
                                className="transition-all duration-1000 ease-out"
                              />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                              <span className="text-white font-bold text-sm">{percentage}%</span>
                            </div>
                          </div>
                        </div>

                        {/* RIGHT: Action */}
                        <Button
                          size="lg"
                          className="bg-white/10 hover:bg-white/20 text-white border border-white/20 backdrop-blur-sm group-hover:bg-white group-hover:text-black transition-all duration-300"
                        >
                          Practice Now
                          <ArrowRight className="ml-2 h-4 w-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>

          {/* RIGHT COLUMN: Topics Sidebar (40% width) */}
          {analysisData.analysis_data.topics.length > 0 && (
            <div className="col-span-12 lg:col-span-5 xl:col-span-4">
              <div className="sticky top-8 space-y-6">
                <h2 className="text-xl font-semibold text-white mb-6" style={{ textShadow: '0 0 15px rgba(255, 255, 255, 0.5)' }}>
                  Knowledge Areas
                </h2>

                {/* Vertical scrollable topics list */}
                <div className="max-h-[60vh] overflow-y-auto custom-scrollbar space-y-3">
                  {analysisData.analysis_data.topics.map((topic, index) => (
                    <Card
                      key={index}
                      className="bg-gray-900/60 border-gray-700/50 backdrop-blur-sm hover:bg-gray-800/60 transition-all duration-200"
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-3">
                          <h4 className="font-medium text-white text-sm leading-tight">
                            {topic.topic_name}
                          </h4>
                          <span className="text-xs bg-blue-900/50 text-blue-300 px-2 py-1 rounded shrink-0 ml-2">
                            {topic.question_count}
                          </span>
                        </div>

                        {topic.keywords && topic.keywords.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {topic.keywords.slice(0, 3).map((keyword, i) => (
                              <span key={i} className="text-xs bg-gray-800/80 text-gray-300 px-2 py-1 rounded">
                                {keyword}
                              </span>
                            ))}
                            {topic.keywords.length > 3 && (
                              <span className="text-xs text-gray-500">+{topic.keywords.length - 3}</span>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  )
}