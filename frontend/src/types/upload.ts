export interface UploadFile {
  id: string
  file: File
  status: 'pending' | 'uploading' | 'success' | 'error'
  progress: number
  error?: string
}

export interface UploadState {
  files: UploadFile[]
  isDragOver: boolean
}