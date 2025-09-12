import { useState, useCallback, DragEvent } from 'react'
import { UploadFile } from '@/types/upload'

const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB
const MAX_FILES = 5
const ALLOWED_TYPES = ['application/pdf']

export function useDropZone() {
  const [isDragOver, setIsDragOver] = useState(false)
  const [files, setFiles] = useState<UploadFile[]>([])

  const validateFile = (file: File): string | null => {
    if (!ALLOWED_TYPES.includes(file.type)) {
      return 'Only PDF files are allowed'
    }
    if (file.size > MAX_FILE_SIZE) {
      return 'File size must be less than 10MB'
    }
    return null
  }

  const addFiles = useCallback((newFiles: File[]) => {
    const validFiles: UploadFile[] = []
    
    for (const file of newFiles) {
      // Check if we've reached the limit
      if (files.length + validFiles.length >= MAX_FILES) {
        alert(`Maximum ${MAX_FILES} files allowed`)
        break
      }

      // Check if file already exists
      const exists = files.some(f => f.file.name === file.name && f.file.size === file.size)
      if (exists) {
        continue
      }

      const error = validateFile(file)
      validFiles.push({
        id: Math.random().toString(36).substr(2, 9),
        file,
        status: error ? 'error' : 'pending',
        progress: 0,
        error
      })
    }

    setFiles(prev => [...prev, ...validFiles])
  }, [files])

  const removeFile = useCallback((id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id))
  }, [])

  const handleDragOver = useCallback((e: DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback((e: DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    
    const droppedFiles = Array.from(e.dataTransfer.files)
    addFiles(droppedFiles)
  }, [addFiles])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files)
      addFiles(selectedFiles)
    }
  }, [addFiles])

  return {
    isDragOver,
    files,
    handleDragOver,
    handleDragLeave,
    handleDrop,
    handleFileSelect,
    removeFile,
    setFiles
  }
}