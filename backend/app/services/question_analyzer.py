import re
import logging
from typing import List, Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import uuid

import numpy as np
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.cluster import HDBSCAN
    from bertopic import BERTopic
except ImportError:
    SentenceTransformer = None
    HDBSCAN = None
    BERTopic = None

from app.core.config import settings

logger = logging.getLogger(__name__)


class QuestionAnalyzer:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.model = None
        self.topic_model = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models"""
        try:
            if SentenceTransformer:
                self.model = SentenceTransformer(settings.SENTENCE_TRANSFORMER_MODEL)
                logger.info("Sentence transformer model loaded successfully")
            else:
                logger.warning("sentence-transformers not available, using basic analysis")
                
            if BERTopic:
                self.topic_model = BERTopic(verbose=True)
                logger.info("BERTopic model initialized")
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        """Analyze text and extract questions with topics"""
        try:
            # Extract questions from text
            questions = await self._extract_questions(text)
            
            if not questions:
                return {
                    "questions": [],
                    "topics": [],
                    "clusters": [],
                    "summary": {"total_questions": 0, "topics_found": 0}
                }
            
            # Classify and cluster questions
            classified_questions = await self._classify_questions(questions)
            
            # Extract topics if we have enough questions
            topics = []
            clusters = []
            if len(questions) >= 3 and self.model:
                topics, clusters = await self._extract_topics(questions)
            
            return {
                "questions": classified_questions,
                "topics": topics,
                "clusters": clusters,
                "summary": {
                    "total_questions": len(questions),
                    "topics_found": len(topics)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in question analysis: {str(e)}")
            return {"error": str(e), "questions": [], "topics": []}
    
    async def _extract_questions(self, text: str) -> List[str]:
        """Extract individual questions from text"""
        def _extract():
            questions = []
            
            # Common question patterns
            patterns = [
                r'\d+\.?\s*(.+?\?)',  # Numbered questions ending with ?
                r'Question\s*\d+[:\.]?\s*(.+?)(?=Question\s*\d+|\Z)',  # Questions with "Question N:"
                r'Q\d+[:\.]?\s*(.+?)(?=Q\d+|\Z)',  # Questions with "Q1:"
                r'^(.+?\?)$',  # Any line ending with ?
                r'([A-Z][^.!?]*\?)',  # Sentences ending with ?
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.MULTILINE | re.IGNORECASE | re.DOTALL)
                for match in matches:
                    question = match.strip()
                    if len(question) > 10 and question not in questions:  # Filter short matches
                        questions.append(question)
            
            # Also try splitting by common separators
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if ('?' in line and len(line) > 15 and 
                    any(word in line.lower() for word in ['what', 'how', 'why', 'when', 'where', 'which', 'who'])):
                    if line not in questions:
                        questions.append(line)
            
            # Remove duplicates and clean
            unique_questions = []
            for q in questions:
                q_clean = re.sub(r'\s+', ' ', q).strip()
                if q_clean and len(q_clean) > 10:
                    unique_questions.append(q_clean)
            
            return list(set(unique_questions))
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _extract)
    
    async def _classify_questions(self, questions: List[str]) -> List[Dict[str, Any]]:
        """Classify questions by type and difficulty"""
        def _classify():
            classified = []
            
            for i, question in enumerate(questions):
                question_data = {
                    "question_id": str(uuid.uuid4()),
                    "question_text": question,
                    "question_type": self._determine_question_type(question),
                    "topic": "General",  # Will be updated by clustering
                    "difficulty": self._estimate_difficulty(question),
                    "confidence_score": 0.8
                }
                classified.append(question_data)
            
            return classified
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _classify)
    
    def _determine_question_type(self, question: str) -> str:
        """Determine the type of question"""
        question_lower = question.lower()
        
        # Multiple choice indicators
        if any(indicator in question_lower for indicator in ['a)', 'b)', 'c)', 'd)', 'a.', 'b.', 'c.', 'd.']):
            return "multiple_choice"
        
        # True/false indicators
        if any(indicator in question_lower for indicator in ['true or false', 'true/false', 't/f']):
            return "true_false"
        
        # Fill in the blank
        if '___' in question or 'fill in' in question_lower:
            return "fill_in_blank"
        
        # Short answer keywords
        if any(word in question_lower for word in ['explain', 'describe', 'discuss', 'analyze']):
            return "short_answer"
        
        # Essay indicators
        if any(word in question_lower for word in ['essay', 'elaborate', 'critically evaluate']):
            return "essay"
        
        # Default to short answer
        return "short_answer"
    
    def _estimate_difficulty(self, question: str) -> str:
        """Estimate question difficulty based on complexity"""
        # Simple heuristics
        word_count = len(question.split())
        complex_words = ['analyze', 'evaluate', 'synthesize', 'compare', 'contrast', 'critically']
        
        if any(word in question.lower() for word in complex_words):
            return "hard"
        elif word_count > 20:
            return "medium"
        else:
            return "easy"
    
    async def _extract_topics(self, questions: List[str]) -> tuple:
        """Extract topics using ML clustering"""
        def _extract():
            try:
                if not self.model:
                    return [], []
                
                # Generate embeddings
                embeddings = self.model.encode(questions)
                
                # Cluster questions
                if HDBSCAN:
                    clusterer = HDBSCAN(min_cluster_size=2, min_samples=1)
                    cluster_labels = clusterer.fit_predict(embeddings)
                else:
                    # Fallback to simple clustering
                    from sklearn.cluster import KMeans
                    n_clusters = min(len(questions) // 2, 5)
                    clusterer = KMeans(n_clusters=n_clusters, random_state=42)
                    cluster_labels = clusterer.fit_predict(embeddings)
                
                # Extract topics using BERTopic if available
                topics = []
                clusters = []
                
                if self.topic_model and len(questions) >= 5:
                    try:
                        topics_data, probabilities = self.topic_model.fit_transform(questions)
                        topic_info = self.topic_model.get_topic_info()
                        
                        for idx, row in topic_info.iterrows():
                            if row['Topic'] != -1:  # Skip outlier topic
                                topics.append({
                                    "topic_id": f"topic_{row['Topic']}",
                                    "topic_name": f"Topic {row['Topic']}",
                                    "keywords": [word for word, score in self.topic_model.get_topic(row['Topic'])[:5]],
                                    "question_count": row['Count'],
                                    "confidence_score": 0.7
                                })
                    except Exception as e:
                        logger.error(f"BERTopic failed: {str(e)}")
                
                # Create cluster information
                unique_labels = set(cluster_labels)
                for label in unique_labels:
                    if label != -1:  # Skip noise points
                        cluster_questions = [q for i, q in enumerate(questions) if cluster_labels[i] == label]
                        clusters.append({
                            "cluster_id": f"cluster_{label}",
                            "questions": cluster_questions,
                            "size": len(cluster_questions)
                        })
                
                return topics, clusters
                
            except Exception as e:
                logger.error(f"Error in topic extraction: {str(e)}")
                return [], []
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _extract)