import { useRef } from 'react'
import { Upload, X, FileText, AlertCircle, CheckCircle2 } from 'lucide-react'
import { Button } from './ui/button'
import { Card, CardContent } from './ui/card'
import { Progress } from './ui/progress'
import { useDropZone } from '../hooks/useDropZone'
import { cn } from '../lib/utils'

export function UploadSection() {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { 
    isDragOver, 
    files, 
    handleDragOver, 
    handleDragLeave, 
    handleDrop, 
    handleFileSelect, 
    removeFile 
  } = useDropZone()

  const handleButtonClick = () => {
    fileInputRef.current?.click()
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      handleButtonClick()
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
    <section className="max-w-4xl mx-auto">
      <Card className="mb-8 bg-gray-900/80 border-gray-700">
        <CardContent className="p-8">
          <div
            className={cn(
              "relative border-2 border-dashed rounded-lg p-12 text-center transition-all duration-200 focus-within:ring-2 focus-within:ring-white focus-within:ring-offset-2 focus-within:ring-offset-gray-900",
              isDragOver 
                ? "border-white bg-gray-800/50 shadow-[0_0_30px_rgba(255,255,255,0.2)]" 
                : "border-gray-600 hover:border-gray-500"
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onKeyDown={handleKeyDown}
            tabIndex={0}
            role="button"
            aria-label="Click to upload PDF files or drag and drop them here"
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".pdf"
              onChange={handleFileSelect}
              className="sr-only"
              id="file-upload"
              aria-describedby="file-upload-description"
            />
            
            <Upload 
              className={cn(
                "mx-auto mb-4 h-12 w-12 transition-colors",
                isDragOver ? "text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.8)]" : "text-gray-400"
              )} 
            />
            
            <h3 className="text-xl font-semibold text-white mb-2" style={{ textShadow: '0 0 20px rgba(255, 255, 255, 0.6)' }}>
              {isDragOver ? "Drop your files here" : "Upload your exam PDFs"}
            </h3>
            
            <p className="text-gray-300 mb-6" style={{ textShadow: '0 0 10px rgba(255, 255, 255, 0.3)' }}>
              Drag and drop your PDF files here, or click to browse
            </p>
            
            <Button 
              onClick={handleButtonClick} 
              size="lg" 
              className="mb-4"
              aria-describedby="file-upload-description"
            >
              Choose Files
            </Button>
            
            <div id="file-upload-description" className="text-sm text-gray-400 space-y-1" style={{ textShadow: '0 0 8px rgba(255, 255, 255, 0.2)' }}>
              <p>• PDF files only, up to 10MB each</p>
              <p>• Maximum 5 files at once</p>
              <p>• Files are processed securely and deleted after analysis</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {files.length > 0 && (
        <Card className="bg-gray-900/80 border-gray-700">
          <CardContent className="p-6">
            <h4 className="text-lg font-semibold mb-4 text-white" style={{ textShadow: '0 0 15px rgba(255, 255, 255, 0.5)' }}>
              Uploaded Files ({files.length}/5)
            </h4>
            <div className="space-y-4">
              {files.map((uploadFile) => (
                <div 
                  key={uploadFile.id}
                  className="flex items-center space-x-4 p-4 border border-gray-700 rounded-lg bg-gray-800/50"
                >
                  {getStatusIcon(uploadFile.status)}
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-medium text-white truncate" style={{ textShadow: '0 0 10px rgba(255, 255, 255, 0.3)' }}>
                        {uploadFile.file.name}
                      </p>
                      <p className="text-sm text-gray-400">
                        {formatFileSize(uploadFile.file.size)}
                      </p>
                    </div>
                    
                    {uploadFile.status === 'uploading' && (
                      <Progress value={uploadFile.progress} className="h-2" />
                    )}
                    
                    {uploadFile.error && (
                      <p className="text-sm text-red-400 mt-1">
                        {uploadFile.error}
                      </p>
                    )}
                    
                    {uploadFile.status === 'success' && (
                      <p className="text-sm text-green-400 mt-1">
                        Upload complete
                      </p>
                    )}
                  </div>
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(uploadFile.id)}
                    className="text-gray-400 hover:text-white hover:bg-gray-700"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
            
            {files.some(f => f.status === 'pending' || f.status === 'success') && (
              <div className="mt-6 flex justify-center">
                <Button size="lg" className="px-8">
                  Analyze Files
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </section>
  )
}