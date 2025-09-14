import { useLocation, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { ArrowLeft, Upload, FileText, BarChart3, Target, Brain, PieChart } from 'lucide-react'
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
      {/* Header */}
      <div className="border-b border-gray-800">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleBackToUpload}
                className="text-gray-400 hover:text-white hover:bg-gray-800"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Upload
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-white" style={{ textShadow: '0 0 15px rgba(255, 255, 255, 0.5)' }}>
                  Analysis Results
                </h1>
                <p className="text-gray-400">
                  {analysisData.filename || 'Document'} • {analysisData.analysis_data.summary.total_questions} questions analyzed
                </p>
              </div>
            </div>
            <Button
              onClick={handleNewUpload}
              className="bg-white text-black hover:bg-gray-200"
            >
              <Upload className="h-4 w-4 mr-2" />
              Analyze Another File
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="bg-gray-900/80 border-gray-700">
            <CardContent className="p-6 text-center">
              <FileText className="h-8 w-8 text-white mx-auto mb-2" />
              <div className="text-3xl font-bold text-white" style={{ textShadow: '0 0 15px rgba(255, 255, 255, 0.5)' }}>
                {analysisData.analysis_data.summary.total_questions}
              </div>
              <div className="text-gray-300">Total Questions</div>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/80 border-gray-700">
            <CardContent className="p-6 text-center">
              <PieChart className="h-8 w-8 text-blue-400 mx-auto mb-2" />
              <div className="text-3xl font-bold text-white" style={{ textShadow: '0 0 15px rgba(255, 255, 255, 0.5)' }}>
                {analysisData.analysis_data.topics.length}
              </div>
              <div className="text-gray-300">Topics Identified</div>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/80 border-gray-700">
            <CardContent className="p-6 text-center">
              <Target className="h-8 w-8 text-green-400 mx-auto mb-2" />
              <div className="text-3xl font-bold text-white" style={{ textShadow: '0 0 15px rgba(255, 255, 255, 0.5)' }}>
                {questionTypeStats.length}
              </div>
              <div className="text-gray-300">Question Types</div>
            </CardContent>
          </Card>

          <Card className="bg-gray-900/80 border-gray-700">
            <CardContent className="p-6 text-center">
              <Brain className="h-8 w-8 text-purple-400 mx-auto mb-2" />
              <div className="text-3xl font-bold text-white" style={{ textShadow: '0 0 15px rgba(255, 255, 255, 0.5)' }}>
                {analysisData.status === 'completed' ? '100%' : '0%'}
              </div>
              <div className="text-gray-300">Analysis Complete</div>
            </CardContent>
          </Card>
        </div>

        {/* Question Type Cards */}
        <div>
          <h2 className="text-xl font-semibold text-white mb-6" style={{ textShadow: '0 0 15px rgba(255, 255, 255, 0.5)' }}>
            Question Types Breakdown
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {questionTypeStats.map(({ type, count, percentage }) => (
              <Card 
                key={type} 
                className={`cursor-pointer transition-all duration-200 hover:scale-[1.02] hover:shadow-2xl bg-gradient-to-br ${getQuestionTypeColor(type)} border hover:border-opacity-80 group`}
                onClick={() => handlePracticeQuestionType(type)}
              >
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center justify-between text-white">
                    <div className="flex items-center space-x-3">
                      {getQuestionTypeIcon(type)}
                      <span>{formatQuestionType(type)}</span>
                    </div>
                    <span className="text-2xl font-bold">{count}</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-gray-300">{percentage}% of total</span>
                    <div className="w-16 bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-white rounded-full h-2 transition-all duration-500"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                  <div className="flex justify-center">
                    <Button 
                      size="sm" 
                      variant="ghost" 
                      className="text-white hover:bg-white/10 opacity-80 group-hover:opacity-100 transition-opacity"
                      onClick={(e) => {
                        e.stopPropagation()
                        handlePracticeQuestionType(type)
                      }}
                    >
                      Practice Questions →
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Topics Overview */}
        {analysisData.analysis_data.topics.length > 0 && (
          <div>
            <h2 className="text-xl font-semibold text-white mb-6" style={{ textShadow: '0 0 15px rgba(255, 255, 255, 0.5)' }}>
              Topics Covered
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {analysisData.analysis_data.topics.map((topic, index) => (
                <Card key={index} className="bg-gray-900/80 border-gray-700">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-white flex items-center justify-between">
                      <span>{topic.topic_name}</span>
                      <span className="text-sm bg-blue-900/50 text-blue-300 px-2 py-1 rounded">
                        {topic.question_count} questions
                      </span>
                    </CardTitle>
                  </CardHeader>
                  {topic.keywords && topic.keywords.length > 0 && (
                    <CardContent className="pt-0">
                      <div className="flex flex-wrap gap-2">
                        {topic.keywords.map((keyword, i) => (
                          <span
                            key={i}
                            className="text-xs bg-gray-800 text-gray-300 px-2 py-1 rounded"
                          >
                            {keyword}
                          </span>
                        ))}
                      </div>
                    </CardContent>
                  )}
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}