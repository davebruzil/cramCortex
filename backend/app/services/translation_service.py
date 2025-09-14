import asyncio
import logging
from typing import Dict, Any, Optional

from .hebrew_translator import HebrewTranslator

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Main service for handling document translation workflows.
    Provides high-level translation functions that can be integrated
    into the document processing pipeline.
    """

    def __init__(self):
        self.hebrew_translator = HebrewTranslator()

    async def translate_document(
        self,
        content: str,
        source_language: str = "auto",
        target_language: str = "english",
        document_type: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Main function to translate document content from source to target language.

        Args:
            content: The text content to translate
            source_language: Source language ('hebrew', 'auto', etc.)
            target_language: Target language ('english' currently supported)
            document_type: Type of document for context-aware translation

        Returns:
            Dict with translation results and metadata
        """
        try:
            logger.info(f"Starting document translation: {source_language} -> {target_language}")
            logger.info(f"Document type: {document_type}, Content length: {len(content)} characters")

            # Currently only Hebrew to English is supported
            if target_language.lower() != "english":
                logger.warning(f"Target language '{target_language}' not supported, defaulting to English")

            # Auto-detect or process Hebrew content
            if source_language.lower() in ["hebrew", "auto"]:
                result = await self.hebrew_translator.translate_document_content(
                    document_content=content,
                    document_type=document_type
                )

                # Add service metadata
                result.update({
                    "service": "TranslationService",
                    "source_language": "hebrew" if result.get("has_hebrew") else "unknown",
                    "target_language": "english",
                    "translation_method": "llm_chunked"
                })

                return result
            else:
                logger.warning(f"Source language '{source_language}' not supported")
                return {
                    "translated_text": content,
                    "success": False,
                    "error": f"Source language '{source_language}' not supported",
                    "service": "TranslationService"
                }

        except Exception as e:
            logger.error(f"Error in document translation: {str(e)}")
            return {
                "translated_text": content,
                "success": False,
                "error": str(e),
                "service": "TranslationService"
            }

    async def translate_exam_document(self, content: str) -> Dict[str, Any]:
        """
        Specialized function for translating exam/test documents.
        Optimized for preserving question structure and formatting.

        Args:
            content: The exam content to translate

        Returns:
            Translation result with exam-specific metadata
        """
        logger.info("Processing exam document for translation")

        result = await self.translate_document(
            content=content,
            source_language="auto",
            target_language="english",
            document_type="exam"
        )

        # Add exam-specific metadata
        if result.get("success"):
            result.update({
                "document_category": "educational",
                "preserves_structure": True,
                "optimized_for": "question_format"
            })

        return result

    async def batch_translate_chunks(self, chunks: list, chunk_metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Translate multiple text chunks in batch, useful for large documents
        that have been pre-processed into sections.

        Args:
            chunks: List of text chunks to translate
            chunk_metadata: Optional metadata about the chunks

        Returns:
            Dict with batch translation results
        """
        try:
            logger.info(f"Starting batch translation of {len(chunks)} chunks")

            translated_chunks = []
            failed_chunks = []

            # Process chunks with concurrency control
            semaphore = asyncio.Semaphore(3)  # Limit concurrent translations

            async def translate_single_chunk(chunk_data):
                chunk_text, index = chunk_data
                async with semaphore:
                    try:
                        result = await self.hebrew_translator.translate_hebrew_to_english(chunk_text)
                        return index, result
                    except Exception as e:
                        logger.error(f"Failed to translate chunk {index}: {str(e)}")
                        return index, {"success": False, "error": str(e), "translated_text": chunk_text}

            # Execute batch translation
            chunk_tasks = [(chunk, i) for i, chunk in enumerate(chunks)]
            results = await asyncio.gather(*[translate_single_chunk(chunk_data) for chunk_data in chunk_tasks])

            # Process results
            for index, result in results:
                if result.get("success"):
                    translated_chunks.append({
                        "index": index,
                        "original": chunks[index],
                        "translated": result["translated_text"],
                        "metadata": result
                    })
                else:
                    failed_chunks.append({
                        "index": index,
                        "original": chunks[index],
                        "error": result.get("error", "Unknown error")
                    })

            # Combine all translated text
            combined_translation = "\n\n".join([chunk["translated"] for chunk in translated_chunks])

            success_rate = len(translated_chunks) / len(chunks) if chunks else 0

            return {
                "translated_text": combined_translation,
                "success": success_rate > 0.5,  # Consider successful if > 50% chunks translated
                "total_chunks": len(chunks),
                "successful_chunks": len(translated_chunks),
                "failed_chunks": len(failed_chunks),
                "success_rate": success_rate,
                "chunk_details": translated_chunks,
                "failed_chunk_details": failed_chunks,
                "service": "TranslationService",
                "method": "batch_translation"
            }

        except Exception as e:
            logger.error(f"Error in batch translation: {str(e)}")
            return {
                "translated_text": "\n\n".join(chunks),  # Return original on error
                "success": False,
                "error": str(e),
                "service": "TranslationService"
            }

    async def test_service(self) -> Dict[str, bool]:
        """
        Test all translation capabilities of the service

        Returns:
            Dict with test results for different service components
        """
        logger.info("Testing TranslationService components")

        results = {
            "hebrew_translator": False,
            "document_translation": False,
            "exam_translation": False,
            "batch_translation": False
        }

        try:
            # Test Hebrew translator
            hebrew_test = await self.hebrew_translator.test_translation_service()
            results["hebrew_translator"] = hebrew_test

            # Test document translation
            test_doc = "זהו מסמך לבדיקה עם טקסט בעברית."
            doc_result = await self.translate_document(test_doc, "hebrew", "english")
            results["document_translation"] = doc_result.get("success", False)

            # Test exam translation
            test_exam = "1. מה זה אבטחת מידע? א) הגנה על מחשבים ב) הגנה על נתונים"
            exam_result = await self.translate_exam_document(test_exam)
            results["exam_translation"] = exam_result.get("success", False)

            # Test batch translation
            test_chunks = ["שלום עולם", "זה מבחן של התרגום", "האם זה עובד?"]
            batch_result = await self.batch_translate_chunks(test_chunks)
            results["batch_translation"] = batch_result.get("success", False)

            logger.info(f"Service test results: {results}")

        except Exception as e:
            logger.error(f"Error testing translation service: {str(e)}")

        return results

    def get_supported_languages(self) -> Dict[str, list]:
        """
        Get information about supported source and target languages

        Returns:
            Dict with supported language information
        """
        return {
            "source_languages": ["hebrew", "auto"],
            "target_languages": ["english"],
            "auto_detection": True,
            "batch_processing": True,
            "document_types": ["exam", "text", "document", "unknown"]
        }

    def get_service_info(self) -> Dict[str, Any]:
        """
        Get information about the translation service capabilities

        Returns:
            Dict with service information and capabilities
        """
        return {
            "service_name": "TranslationService",
            "version": "1.0.0",
            "capabilities": {
                "hebrew_to_english": True,
                "chunked_processing": True,
                "batch_translation": True,
                "exam_document_handling": True,
                "structure_preservation": True,
                "concurrent_processing": True,
                "auto_language_detection": True
            },
            "supported_formats": {
                "input": ["text", "string"],
                "output": ["text", "structured_result"]
            },
            "performance": {
                "max_chunk_size": 3000,
                "concurrent_chunks": 3,
                "retry_attempts": 3
            },
            "dependencies": ["OpenAI API", "Hebrew Language Detection"],
            "supported_languages": self.get_supported_languages()
        }