from pydantic import BaseModel
from typing import Dict, Any, List, Optional


class AnalysisRequest(BaseModel):
    document_id: str
    analysis_type: Optional[str] = "full"


class QuestionData(BaseModel):
    question_id: str
    question_text: str
    question_type: str
    topic: str
    difficulty: Optional[str]
    confidence_score: float


class AnalysisResponse(BaseModel):
    document_id: str
    status: str
    questions_found: int
    topics_identified: int
    analysis_data: Dict[str, Any]


class TopicCluster(BaseModel):
    topic_id: str
    topic_name: str
    question_count: int
    keywords: List[str]
    confidence_score: float