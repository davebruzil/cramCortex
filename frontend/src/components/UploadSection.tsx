import { useRef, useState, useCallback, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, X, FileText, AlertCircle, CheckCircle2, Brain, CloudUpload, Sparkles, Zap } from 'lucide-react'
import { Button } from './ui/button'
import { Card, CardContent } from './ui/card'
import { Progress } from './ui/progress'
import { useDropZone } from '../hooks/useDropZone'
import { cn } from '../lib/utils'
import { apiService, type AnalysisResponse } from '../services/api'

export function UploadSection() {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResults, setAnalysisResults] = useState<AnalysisResponse[]>([])

  const {
    isDragOver,
    files,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleFileSelect,
    removeFile,
    setFiles
  } = useDropZone()

  // Auto-trigger analysis when files are added via drag and drop
  useEffect(() => {
    const pendingFiles = files.filter(f => f.status === 'pending')
    if (pendingFiles.length > 0 && !isAnalyzing) {
      // Small delay to ensure state is stable
      setTimeout(() => {
        handleAnalyze()
      }, 100)
    }
  }, [files.length]) // Only trigger when files count changes

  const handleButtonClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileSelectAndAnalyze = async (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFileSelect(e)

    // Auto-analyze after a brief delay to let file selection complete
    setTimeout(async () => {
      // Get the fresh files from the event
      const selectedFiles = Array.from(e.target.files || [])
      if (selectedFiles.length > 0) {
        await handleAnalyze()
      }
    }, 100)
  }

  const handleAnalyze = async () => {
    if (isAnalyzing) return

    setIsAnalyzing(true)
    const results: AnalysisResponse[] = []

    try {
      // Process files that are pending or have been successfully uploaded
      const filesToProcess = files.filter(f => f.status === 'pending' || f.status === 'success')

      for (const uploadFile of filesToProcess) {
        try {
          // Update file status to uploading
          setFiles(prev => prev.map(f =>
            f.id === uploadFile.id
              ? { ...f, status: 'uploading', progress: 10 }
              : f
          ))

          // Upload file to backend
          const uploadResponse = await apiService.uploadDocument(uploadFile.file)

          // Update progress
          setFiles(prev => prev.map(f =>
            f.id === uploadFile.id
              ? { ...f, progress: 50 }
              : f
          ))

          // Analyze the uploaded document
          const analysisResponse = await apiService.analyzeDocument(uploadResponse.document_id)
          results.push(analysisResponse)

          // Update file status to success
          setFiles(prev => prev.map(f =>
            f.id === uploadFile.id
              ? { ...f, status: 'success', progress: 100 }
              : f
          ))

        } catch (error) {
          // Update file status to error
          setFiles(prev => prev.map(f =>
            f.id === uploadFile.id
              ? {
                  ...f,
                  status: 'error',
                  error: error instanceof Error ? error.message : 'Analysis failed',
                  progress: 0
                }
              : f
          ))

          console.error(`Error processing ${uploadFile.file.name}:`, error)
        }
      }

      setAnalysisResults(results)

      // Navigate to results page if we have successful analysis
      if (results.length > 0) {
        // For now, navigate with the first result (in case multiple files)
        const firstResult = results[0]
        navigate('/results', {
          state: {
            analysisData: {
              ...firstResult,
              filename: filesToProcess[0]?.file.name
            }
          }
        })
      }

    } catch (error) {
      console.error('Analysis error:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      case 'uploading':
        return <div className="h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      default:
        return <FileText className="h-4 w-4 text-gray-500" />
    }
  }

  return (
    <section className="max-w-2xl mx-auto">
      {/* File Counter Display */}
      {files.length > 0 && (
        <div className="text-center mb-6">
          <p className={`text-sm font-medium ${files.length >= 5 ? 'text-yellow-300' : 'text-white/80'}`}
             style={{ textShadow: '0 0 15px rgba(255, 255, 255, 0.6)' }}>
            {files.length}/5 files uploaded
            {files.length >= 5 && <span className="ml-2 text-yellow-400">(Maximum reached)</span>}
          </p>
        </div>
      )}

      {/* JUST THE BIG ORBITAL BUTTON */}
      <div className="flex justify-center py-12">
        <div
          onClick={handleButtonClick}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={cn(
            "group relative w-40 h-40 cursor-pointer",
            "transition-all duration-500 ease-out",
            "hover:scale-125 active:scale-95",
            isDragOver ? "scale-150" : ""
          )}
          aria-label="Upload your PDF files"
          role="button"
          tabIndex={0}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf"
            onChange={handleFileSelectAndAnalyze}
            className="sr-only"
          />

          {/* Dynamic rings - normal vs loading state */}
          {isAnalyzing ? (
            // LOADING ANIMATION - Intense radiating circles
            <>
              <div className="absolute inset-0 rounded-full border-2 border-white/40 animate-spin" style={{ animationDuration: '0.8s' }}></div>
              <div className="absolute -inset-2 rounded-full border border-white/30 animate-ping" style={{ animationDuration: '0.4s' }}></div>
              <div className="absolute -inset-4 rounded-full border border-white/25 animate-ping" style={{ animationDuration: '0.6s', animationDelay: '0.1s' }}></div>
              <div className="absolute -inset-8 rounded-full border border-white/20 animate-ping" style={{ animationDuration: '0.8s', animationDelay: '0.2s' }}></div>
              <div className="absolute -inset-12 rounded-full border border-white/15 animate-ping" style={{ animationDuration: '1.0s', animationDelay: '0.3s' }}></div>
              <div className="absolute -inset-16 rounded-full border border-white/12 animate-ping" style={{ animationDuration: '1.2s', animationDelay: '0.4s' }}></div>
              <div className="absolute -inset-20 rounded-full border border-white/10 animate-ping" style={{ animationDuration: '1.4s', animationDelay: '0.5s' }}></div>
              <div className="absolute -inset-24 rounded-full border border-white/8 animate-ping" style={{ animationDuration: '1.6s', animationDelay: '0.6s' }}></div>
              <div className="absolute -inset-32 rounded-full border border-white/6 animate-ping" style={{ animationDuration: '1.8s', animationDelay: '0.7s' }}></div>
              <div className="absolute -inset-40 rounded-full border border-white/4 animate-ping" style={{ animationDuration: '2.0s', animationDelay: '0.8s' }}></div>
            </>
          ) : (
            // NORMAL STATE - Clean evenly spaced rings
            <>
              <div className="absolute inset-0 rounded-full border border-white/12 animate-ping" style={{ animationDuration: '2s' }}></div>
              <div className="absolute -inset-6 rounded-full border border-white/10 animate-ping" style={{ animationDuration: '2s', animationDelay: '0.3s' }}></div>
              <div className="absolute -inset-12 rounded-full border border-white/8 animate-ping" style={{ animationDuration: '2s', animationDelay: '0.6s' }}></div>
              <div className="absolute -inset-18 rounded-full border border-white/6 animate-ping" style={{ animationDuration: '2s', animationDelay: '0.9s' }}></div>
              <div className="absolute -inset-24 rounded-full border border-white/4 animate-ping" style={{ animationDuration: '2s', animationDelay: '1.2s' }}></div>
            </>
          )}

          {/* Outer spinning orbital ring */}
          <div className="absolute inset-0 rounded-full"
               style={{
                 animation: 'spin 15s linear infinite',
                 background: 'conic-gradient(from 0deg, transparent, rgba(255,255,255,0.4), transparent)'
               }}></div>

          {/* Inner pulsing core - loading state */}
          <div className={cn(
            "absolute inset-6 rounded-full transition-colors duration-500",
            isAnalyzing
              ? "bg-white/40 animate-pulse"
              : "bg-white/20 animate-pulse group-hover:bg-white/40"
          )}></div>

          {/* Central brain button - loading state */}
          <div className={cn(
            "absolute inset-12 rounded-full transition-all duration-700 flex items-center justify-center",
            isAnalyzing
              ? "bg-gradient-to-br from-white via-white/95 to-white/90 shadow-[0_0_60px_rgba(255,255,255,1),0_0_120px_rgba(255,255,255,0.6)]"
              : cn(
                  "bg-gradient-to-br from-white/95 via-white/90 to-white/80",
                  "group-hover:from-gray-100/95 group-hover:via-gray-100/85 group-hover:to-gray-100/70",
                  "group-hover:shadow-[0_0_40px_rgba(255,255,255,0.8),0_0_80px_rgba(255,255,255,0.4)]",
                  isDragOver ? "from-blue-100/90 via-blue-100/80 to-blue-100/60 shadow-[0_0_60px_rgba(59,130,246,0.6)]" : ""
                )
          )}>
            <Brain className={cn(
              "transition-all duration-500",
              isAnalyzing
                ? "h-12 w-12 text-black animate-spin scale-110"
                : cn(
                    "h-11 w-11 text-black/90",
                    "group-hover:animate-pulse group-hover:scale-105 group-hover:text-black",
                    isDragOver ? "text-blue-700 animate-bounce scale-110" : ""
                  )
            )} />
          </div>

          {/* Loading garnishes around brain - only show when analyzing */}
          {isAnalyzing && (
            <>
              {/* Spinning garnish rings */}
              <div className="absolute inset-8 rounded-full border-l-2 border-white/60 animate-spin" style={{ animationDuration: '1.5s' }}></div>
              <div className="absolute inset-10 rounded-full border-r-2 border-white/40 animate-spin" style={{ animationDuration: '2s', animationDirection: 'reverse' }}></div>
              <div className="absolute inset-14 rounded-full border-t-2 border-white/30 animate-spin" style={{ animationDuration: '2.5s' }}></div>


              {/* Pulsing text indicator */}
              <div className="absolute -bottom-16 left-1/2 transform -translate-x-1/2">
                <p className="text-sm text-white animate-pulse font-medium" style={{ textShadow: '0 0 20px rgba(255, 255, 255, 0.8)' }}>
                  Processing...
                </p>
              </div>
            </>
          )}
        </div>
      </div>


      {analysisResults.length > 0 && (
        <Card className="mt-8 bg-gradient-to-br from-gray-900/90 via-gray-800/90 to-gray-900/90 border-gray-700/50 backdrop-blur-md shadow-2xl">
          <CardContent className="p-6">
            <div className="flex items-center space-x-3 mb-6">
              <Brain className="h-6 w-6 text-blue-400" style={{ filter: 'drop-shadow(0 0 15px rgba(96, 165, 250, 0.8))' }} />
              <h4 className="text-2xl font-bold text-white" style={{ textShadow: '0 0 20px rgba(255, 255, 255, 0.6)' }}>
                🎆 Analysis Results
              </h4>
            </div>

            {analysisResults.map((result, index) => (
              <div key={result.document_id} className="mb-6 p-4 border border-gray-600 rounded-lg bg-gray-800/30">
                <div className="flex items-center justify-between mb-4">
                  <h5 className="text-md font-medium text-white">Document {index + 1}</h5>
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    result.status === 'completed'
                      ? 'bg-green-900/50 text-green-300 border border-green-600'
                      : 'bg-yellow-900/50 text-yellow-300 border border-yellow-600'
                  }`}>
                    {result.status}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className="text-center p-3 bg-gray-700/30 rounded-lg">
                    <div className="text-2xl font-bold text-white">{result.questions_found}</div>
                    <div className="text-sm text-gray-300">Questions Found</div>
                  </div>
                  <div className="text-center p-3 bg-gray-700/30 rounded-lg">
                    <div className="text-2xl font-bold text-white">{result.topics_identified}</div>
                    <div className="text-sm text-gray-300">Topics Identified</div>
                  </div>
                  <div className="text-center p-3 bg-gray-700/30 rounded-lg">
                    <div className="text-2xl font-bold text-white">
                      {result.analysis_data?.clusters?.length || 0}
                    </div>
                    <div className="text-sm text-gray-300">Question Clusters</div>
                  </div>
                </div>

                {result.analysis_data?.questions && result.analysis_data.questions.length > 0 && (
                  <div className="mt-4">
                    <h6 className="text-sm font-medium text-white mb-2">Sample Questions:</h6>
                    <div className="space-y-2">
                      {result.analysis_data.questions.slice(0, 3).map((question, qIndex) => (
                        <div key={question.question_id} className="text-sm text-gray-300 bg-gray-700/20 p-2 rounded">
                          <span className="text-blue-400">Q{qIndex + 1}:</span> {question.question_text.substring(0, 100)}
                          {question.question_text.length > 100 && '...'}
                          <div className="flex gap-2 mt-1">
                            <span className="px-1 py-0.5 bg-blue-900/30 text-blue-300 text-xs rounded">
                              {question.question_type}
                            </span>
                            {question.difficulty && (
                              <span className="px-1 py-0.5 bg-purple-900/30 text-purple-300 text-xs rounded">
                                {question.difficulty}
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </section>
  )
}