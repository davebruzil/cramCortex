import logging
from typing import Dict, Any
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class LLMQuestionAnalyzer:
    """
    Enhanced question analyzer powered by GPT-3.5-turbo
    """
    
    def __init__(self):
        self.llm_service = LLMService()
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text using LLM for intelligent question extraction and categorization
        """
        try:
            logger.info(f"Starting LLM-powered analysis of text ({len(text)} characters)")
            
            # Test API connection first
            if not await self.llm_service.test_api_connection():
                logger.error("OpenAI API connection failed, falling back to simple analysis")
                return await self._fallback_analysis(text)
            
            # Use LLM for analysis
            result = await self.llm_service.analyze_text_with_llm(text)
            
            # Validate and enhance the result
            validated_result = self._validate_and_enhance_result(result)
            
            logger.info(f"LLM analysis completed successfully: {len(validated_result['questions'])} questions found")
            return validated_result
            
        except Exception as e:
            logger.error(f"Error in LLM question analysis: {str(e)}")
            # Fall back to simple analysis if LLM fails
            return await self._fallback_analysis(text)
    
    def _validate_and_enhance_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and enhance the LLM result
        """
        # Ensure required fields exist
        if not isinstance(result.get('questions'), list):
            result['questions'] = []
        
        if not isinstance(result.get('topics'), list):
            result['topics'] = []
        
        if not isinstance(result.get('clusters'), list):
            result['clusters'] = []
        
        # Ensure summary exists
        if not isinstance(result.get('summary'), dict):
            result['summary'] = {}
        
        # Update summary stats
        result['summary'].update({
            'total_questions': len(result['questions']),
            'topics_found': len(result['topics'])
        })
        
        # Validate each question has required fields
        for question in result['questions']:
            if not question.get('question_id'):
                question['question_id'] = f"q_{len(result['questions'])}"
            if not question.get('question_text'):
                question['question_text'] = "Question text not available"
            if not question.get('question_type'):
                question['question_type'] = "unknown"
            if not question.get('topic'):
                question['topic'] = "General"
            if not question.get('difficulty'):
                question['difficulty'] = "medium"
            if not question.get('confidence_score'):
                question['confidence_score'] = 0.7
        
        return result
    
    async def _fallback_analysis(self, text: str) -> Dict[str, Any]:
        """
        Simple fallback analysis if LLM is unavailable
        """
        logger.info("Using fallback analysis method")
        
        # Simple question extraction - find lines with question marks
        lines = text.split('\n')
        questions = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if '?' in line and len(line) > 15:
                # Try to determine question type based on simple patterns
                question_type = "unknown"
                
                if any(indicator in line.lower() for indicator in ['a)', 'b)', 'c)', 'd)', '1)', '2)', '3)', '4)']):
                    question_type = "multiple_choice"
                elif any(indicator in line.lower() for indicator in ['true or false', 'true/false', 't/f']):
                    question_type = "true_false"
                elif len(line.split()) > 10:
                    question_type = "short_answer"
                
                questions.append({
                    "question_id": f"fallback_q_{i}",
                    "question_text": line,
                    "question_type": question_type,
                    "topic": "General",
                    "difficulty": "medium",
                    "confidence_score": 0.5
                })
        
        # Create basic topics
        topics = []
        if questions:
            topics.append({
                "topic_id": "topic_0",
                "topic_name": "General",
                "question_count": len(questions),
                "keywords": ["general"],
                "confidence_score": 0.5
            })
        
        return {
            "questions": questions,
            "topics": topics,
            "clusters": [],
            "summary": {
                "total_questions": len(questions),
                "topics_found": len(topics),
                "processing_method": "fallback"
            }
        }