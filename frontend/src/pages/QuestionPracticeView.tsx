import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { ArrowLeft, ArrowRight, ArrowLeftRight, CheckCircle, Clock, Target, BookOpen, EyeOff } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import type { AnalysisResult } from '../types/analysis'

interface Question {
  question_id: string
  question_text: string
  question_type: string
  topic: string
  difficulty: string
  confidence_score: number
  answer_choices?: string[]
  correct_answer?: string
  explanations?: {
    A?: string
    B?: string
    C?: string
    D?: string
  }
  explanation_summary?: string
  keywords: string[]
}

export function QuestionPracticeView() {
  const location = useLocation()
  const navigate = useNavigate()
  const { questionType } = useParams<{ questionType: string }>()
  
  const [analysisData, setAnalysisData] = useState<AnalysisResult | null>(null)
  const [filteredQuestions, setFilteredQuestions] = useState<Question[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [completedQuestions, setCompletedQuestions] = useState<Set<number>>(new Set())
  const [showExplanation, setShowExplanation] = useState(false)

  useEffect(() => {
    // Get analysis data passed from the previous page
    if (location.state?.analysisData) {
      const data = location.state.analysisData
      setAnalysisData(data)
      
      // Filter questions by type
      const filtered = data.analysis_data.questions.filter(
        (q: Question) => q.question_type === questionType
      )
      setFilteredQuestions(filtered)
    } else {
      // If no data, redirect back to home
      navigate('/')
    }
  }, [location.state, questionType, navigate])

  const handleBackToResults = () => {
    navigate('/results', { state: { analysisData } })
  }

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1)
      setShowExplanation(false) // Hide explanation when navigating
    }
  }

  const handleNextQuestion = () => {
    if (currentQuestionIndex < filteredQuestions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
      setShowExplanation(false) // Hide explanation when navigating
    }
  }

  const toggleExplanation = () => {
    setShowExplanation(!showExplanation)
  }

  const handleMarkComplete = () => {
    setCompletedQuestions(prev => new Set([...prev, currentQuestionIndex]))
  }

  const formatQuestionType = (type: string) => {
    return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  const getQuestionTypeIcon = (type: string) => {
    switch (type) {
      case 'multiple_choice':
        return <Target className="h-5 w-5" />
      case 'true_false':
        return <ArrowLeftRight className="h-5 w-5" />
      case 'short_answer':
        return <Clock className="h-5 w-5" />
      default:
        return <CheckCircle className="h-5 w-5" />
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'text-green-400'
      case 'medium':
        return 'text-yellow-400'
      case 'hard':
        return 'text-red-400'
      default:
        return 'text-gray-400'
    }
  }

  if (!analysisData || filteredQuestions.length === 0) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-white" style={{ textShadow: '0 0 10px rgba(255, 255, 255, 0.5)' }}>
            Loading practice questions...
          </p>
        </div>
      </div>
    )
  }

  const currentQuestion = filteredQuestions[currentQuestionIndex]
  const progress = ((currentQuestionIndex + 1) / filteredQuestions.length) * 100
  const completedCount = completedQuestions.size

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <div className="border-b border-gray-800">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleBackToResults}
                className="text-gray-400 hover:text-white hover:bg-gray-800"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Results
              </Button>
              <div className="flex items-center space-x-3">
                {getQuestionTypeIcon(questionType || '')}
                <div>
                  <h1 className="text-xl font-bold text-white" style={{ textShadow: '0 0 15px rgba(255, 255, 255, 0.5)' }}>
                    {formatQuestionType(questionType || '')} Practice
                  </h1>
                  <p className="text-gray-400">
                    Question {currentQuestionIndex + 1} of {filteredQuestions.length} • {completedCount} completed
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Question Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <Card className="bg-gray-900/80 border-gray-700">
          <CardHeader className="pb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <span className="px-3 py-1 bg-blue-900/50 text-blue-300 rounded-full text-sm">
                  {currentQuestion.topic}
                </span>
                <span className={`px-3 py-1 bg-gray-800 rounded-full text-sm ${getDifficultyColor(currentQuestion.difficulty)}`}>
                  {currentQuestion.difficulty}
                </span>
              </div>
              <div className="text-gray-400 text-sm">
                Confidence: {Math.round(currentQuestion.confidence_score * 100)}%
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Question Text */}
            <div className="prose prose-invert max-w-none">
              <h2 className="text-xl text-white leading-relaxed mb-6" style={{ textShadow: '0 0 10px rgba(255, 255, 255, 0.3)' }}>
                {currentQuestion.question_text}
              </h2>
            </div>


            {/* Keywords */}
            {currentQuestion.keywords && currentQuestion.keywords.length > 0 && (
              <div>
                <h3 className="text-sm text-gray-400 mb-2">Related Keywords:</h3>
                <div className="flex flex-wrap gap-2">
                  {currentQuestion.keywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-gray-800 text-gray-300 rounded text-xs"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Answer Choices Card (separate from question) */}
        {currentQuestion.answer_choices && currentQuestion.answer_choices.length > 0 && (
          <Card className="bg-gray-900/80 border-gray-700 mt-6">
            <CardHeader>
              <CardTitle className="text-lg text-white">Answer Options</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3">
                {currentQuestion.answer_choices.map((choice, index) => (
                  <Card key={index} className="bg-gray-800/50 border-gray-600 hover:border-gray-500 transition-colors cursor-pointer">
                    <CardContent className="p-4">
                      <p className="text-gray-200">{choice}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Explanation Button */}
        {currentQuestion.explanations && (
          <div className="flex justify-center mt-6">
            <Button
              onClick={toggleExplanation}
              variant="outline"
              className="text-white border-blue-500 bg-blue-900/30 hover:bg-blue-900/50 hover:border-blue-400"
            >
              {showExplanation ? (
                <>
                  <EyeOff className="h-4 w-4 mr-2" />
                  Hide Explanation
                </>
              ) : (
                <>
                  <BookOpen className="h-4 w-4 mr-2" />
                  Show Explanation
                </>
              )}
            </Button>
          </div>
        )}

        {/* Explanation Section */}
        {showExplanation && currentQuestion.explanations && (
          <Card className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border-blue-500/30 mt-6">
            <CardHeader>
              <CardTitle className="text-lg text-blue-300 flex items-center">
                <BookOpen className="h-5 w-5 mr-2" />
                Answer Explanations
              </CardTitle>
              {currentQuestion.explanation_summary && (
                <p className="text-gray-300 text-sm mt-2">
                  {currentQuestion.explanation_summary}
                </p>
              )}
            </CardHeader>
            <CardContent className="space-y-4">
              {currentQuestion.answer_choices?.map((choice, index) => {
                const letter = String.fromCharCode(65 + index) // A, B, C, D
                const isCorrect = currentQuestion.correct_answer === letter
                const explanation = currentQuestion.explanations?.[letter as keyof typeof currentQuestion.explanations]

                if (!explanation) return null

                return (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border-l-4 ${
                      isCorrect
                        ? 'bg-green-900/20 border-green-400 text-green-100'
                        : 'bg-red-900/20 border-red-400 text-red-100'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      <span
                        className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-bold ${
                          isCorrect
                            ? 'bg-green-500 text-white'
                            : 'bg-red-500 text-white'
                        }`}
                      >
                        {letter}
                      </span>
                      <div className="flex-1">
                        <p className="font-medium mb-2">{choice}</p>
                        <p className="text-sm opacity-90">{explanation}</p>
                      </div>
                      {isCorrect && (
                        <CheckCircle className="h-5 w-5 text-green-400 flex-shrink-0 mt-1" />
                      )}
                    </div>
                  </div>
                )
              })}
            </CardContent>
          </Card>
        )}

        {/* Navigation Controls */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-8">
          <Button
            variant="outline"
            onClick={handlePreviousQuestion}
            disabled={currentQuestionIndex === 0}
            className="text-white border-gray-600 bg-gray-800/50 hover:bg-gray-800 w-full sm:w-auto disabled:opacity-50"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Previous
          </Button>

          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              onClick={handleMarkComplete}
              className={`${
                completedQuestions.has(currentQuestionIndex)
                  ? 'text-green-400 hover:text-green-300'
                  : 'text-gray-400 hover:text-white'
              } w-full sm:w-auto`}
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              <span className="hidden sm:inline">
                {completedQuestions.has(currentQuestionIndex) ? 'Completed' : 'Mark Complete'}
              </span>
              <span className="sm:hidden">
                {completedQuestions.has(currentQuestionIndex) ? '✓' : 'Complete'}
              </span>
            </Button>
          </div>

          <Button
            variant="outline"
            onClick={handleNextQuestion}
            disabled={currentQuestionIndex === filteredQuestions.length - 1}
            className="text-white border-gray-600 bg-gray-800/50 hover:bg-gray-800 w-full sm:w-auto disabled:opacity-50"
          >
            Next
            <ArrowRight className="h-4 w-4 ml-2" />
          </Button>
        </div>
      </div>
    </div>
  )
}