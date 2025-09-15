import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class RAGService:
    """
    Retrieval-Augmented Generation service for cybersecurity knowledge
    """

    def __init__(self):
        self.model = None
        self.knowledge_base = []
        self.embeddings = None
        self.is_initialized = False

    async def initialize(self):
        """Initialize the RAG service with embeddings model and knowledge base"""
        try:
            logger.info("Initializing RAG service...")

            # Load the sentence transformer model
            logger.info("Loading sentence transformer model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')

            # Load cybersecurity knowledge base
            await self._load_knowledge_base()

            # Generate embeddings for knowledge base
            await self._generate_embeddings()

            self.is_initialized = True
            logger.info("RAG service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {str(e)}")
            self.is_initialized = False

    async def _load_knowledge_base(self):
        """Load the cybersecurity knowledge base from JSON file"""
        try:
            knowledge_file = Path(__file__).parent.parent / "data" / "cybersecurity_knowledge.json"

            if not knowledge_file.exists():
                logger.warning(f"Knowledge base file not found: {knowledge_file}")
                return

            with open(knowledge_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.knowledge_base = data.get('cybersecurity_concepts', [])
            logger.info(f"Loaded {len(self.knowledge_base)} knowledge base entries")

        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
            self.knowledge_base = []

    async def _generate_embeddings(self):
        """Generate embeddings for all knowledge base entries"""
        if not self.knowledge_base or not self.model:
            logger.warning("Cannot generate embeddings - missing knowledge base or model")
            return

        try:
            # Create text representations for embedding
            texts = []
            for entry in self.knowledge_base:
                # Combine topic, content, and keywords for comprehensive embedding
                text = f"{entry['topic']}: {entry['content']} Keywords: {', '.join(entry['keywords'])}"
                texts.append(text)

            logger.info(f"Generating embeddings for {len(texts)} knowledge entries...")
            self.embeddings = self.model.encode(texts)
            logger.info("Embeddings generated successfully")

        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            self.embeddings = None

    async def retrieve_relevant_context(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant knowledge base entries for a given query

        Args:
            query: The question or text to find relevant context for
            top_k: Number of top relevant entries to return

        Returns:
            List of relevant knowledge base entries with similarity scores
        """
        if not self.is_initialized or self.embeddings is None:
            logger.warning("RAG service not properly initialized")
            return []

        try:
            # Generate embedding for the query
            query_embedding = self.model.encode([query])

            # Calculate cosine similarity with all knowledge base embeddings
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]

            # Get top-k most similar entries
            top_indices = np.argsort(similarities)[-top_k:][::-1]

            relevant_contexts = []
            for idx in top_indices:
                if similarities[idx] > 0.3:  # Minimum similarity threshold
                    context = self.knowledge_base[idx].copy()
                    context['similarity_score'] = float(similarities[idx])
                    relevant_contexts.append(context)

            logger.info(f"Retrieved {len(relevant_contexts)} relevant contexts for query")
            return relevant_contexts

        except Exception as e:
            logger.error(f"Error retrieving relevant context: {str(e)}")
            return []

    async def enhance_question_with_context(self, question_text: str, answer_choices: List[str]) -> Dict[str, Any]:
        """
        Enhance a question with relevant cybersecurity context for better answer accuracy

        Args:
            question_text: The question text
            answer_choices: List of answer choices

        Returns:
            Dictionary with enhanced context information
        """
        if not self.is_initialized:
            return {"context": "", "confidence_boost": 0.0, "relevant_topics": []}

        # Combine question and answer choices for context retrieval
        full_query = f"{question_text} {' '.join(answer_choices)}"

        # Retrieve relevant context
        relevant_contexts = await self.retrieve_relevant_context(full_query, top_k=3)

        if not relevant_contexts:
            return {"context": "", "confidence_boost": 0.0, "relevant_topics": []}

        # Build context string
        context_parts = []
        relevant_topics = []
        total_confidence = 0.0

        for ctx in relevant_contexts:
            context_parts.append(f"Topic: {ctx['topic']}\nContent: {ctx['content']}")
            relevant_topics.append(ctx['topic'])
            total_confidence += ctx['similarity_score']

        enhanced_context = "\n\n".join(context_parts)
        confidence_boost = min(total_confidence / len(relevant_contexts), 1.0)

        return {
            "context": enhanced_context,
            "confidence_boost": confidence_boost,
            "relevant_topics": relevant_topics,
            "num_contexts": len(relevant_contexts)
        }

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the RAG service"""
        return {
            "initialized": self.is_initialized,
            "knowledge_base_size": len(self.knowledge_base),
            "embeddings_ready": self.embeddings is not None,
            "model_loaded": self.model is not None
        }


# Global RAG service instance
rag_service = RAGService()