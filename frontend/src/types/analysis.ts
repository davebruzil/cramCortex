export interface QuestionData {
  question_id: string
  question_text: string
  question_type: 'multiple_choice' | 'true_false' | 'short_answer' | 'essay' | 'unknown'
  topic: string
  difficulty?: 'easy' | 'medium' | 'hard'
  confidence_score: number
}

export interface TopicData {
  topic_id?: string
  topic_name: string
  question_count: number
  keywords?: string[]
  confidence_score?: number
}

export interface ClusterData {
  cluster_id: string
  questions: string[]
  size: number
}

export interface AnalysisData {
  questions: QuestionData[]
  topics: TopicData[]
  clusters: ClusterData[]
  summary: {
    total_questions: number
    topics_found: number
  }
}

export interface AnalysisResult {
  document_id: string
  filename?: string
  status: string
  questions_found: number
  topics_identified: number
  analysis_data: AnalysisData
}