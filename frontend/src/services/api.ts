const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'

export interface DocumentUploadResponse {
  document_id: string
  filename: string
  file_path: string
  message: string
}

export interface AnalysisResponse {
  document_id: string
  status: string
  questions_found: number
  topics_identified: number
  analysis_data: {
    questions: QuestionData[]
    topics: TopicData[]
    clusters: ClusterData[]
    summary: {
      total_questions: number
      topics_found: number
    }
  }
}

export interface QuestionData {
  question_id: string
  question_text: string
  question_type: string
  topic: string
  difficulty?: string
  confidence_score: number
}

export interface TopicData {
  topic_id: string
  topic_name: string
  keywords: string[]
  question_count: number
  confidence_score: number
}

export interface ClusterData {
  cluster_id: string
  questions: string[]
  size: number
}

export class ApiService {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  async uploadDocument(file: File): Promise<DocumentUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await fetch(`${this.baseUrl}/documents/upload`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`)
    }

    return response.json()
  }

  async analyzeDocument(documentId: string): Promise<AnalysisResponse> {
    const response = await fetch(`${this.baseUrl}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        document_id: documentId,
        analysis_type: 'full'
      }),
    })

    if (!response.ok) {
      throw new Error(`Analysis failed: ${response.statusText}`)
    }

    return response.json()
  }

  async getAnalysisStatus(documentId: string) {
    const response = await fetch(`${this.baseUrl}/analysis/${documentId}/status`)
    
    if (!response.ok) {
      throw new Error(`Status check failed: ${response.statusText}`)
    }

    return response.json()
  }

  async healthCheck() {
    const response = await fetch(`${this.baseUrl}/health`)
    
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`)
    }

    return response.json()
  }
}

export const apiService = new ApiService()