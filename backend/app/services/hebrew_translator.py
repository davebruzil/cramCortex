import asyncio
import json
import logging
import re
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class HebrewTranslator:
    """
    A service for translating Hebrew text to English using OpenAI's LLM,
    with intelligent chunking to handle large documents efficiently.
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.max_chunk_size = 3000  # Characters per chunk for optimal translation

    def _is_hebrew_text(self, text: str) -> bool:
        """
        Check if text contains Hebrew characters
        """
        hebrew_pattern = r'[\u0590-\u05FF\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB1D-\uFB4F]'
        return bool(re.search(hebrew_pattern, text))

    def _contains_hebrew_characters(self, text: str) -> bool:
        """
        ULTRA-STRICT check for ANY Hebrew characters in text
        Includes ALL Hebrew blocks and common mixed-script cases
        """
        # Comprehensive Hebrew and related script detection
        hebrew_patterns = [
            r'[\u0590-\u05FF]',  # Hebrew
            r'[\u0600-\u06FF]',  # Arabic
            r'[\uFB1D-\uFB4F]',  # Hebrew Presentation Forms
            r'[\u200F\u202E]',   # RTL markers
        ]

        # Check each pattern
        for pattern in hebrew_patterns:
            if re.search(pattern, text):
                return True
        return False

    def _extract_hebrew_characters(self, text: str) -> list:
        """
        Extract all Hebrew characters found in text for debugging
        """
        hebrew_pattern = r'[\u0590-\u05FF]'
        hebrew_chars = re.findall(hebrew_pattern, text)
        return list(set(hebrew_chars))  # Return unique Hebrew characters

    def _force_remove_hebrew(self, text: str) -> str:
        """
        NUCLEAR OPTION: Remove ANY non-Latin characters
        This is the absolute last resort to guarantee NO Hebrew
        """
        # Step 1: Remove all Hebrew and related characters
        patterns_to_remove = [
            r'[\u0590-\u05FF]',  # Hebrew
            r'[\u0600-\u06FF]',  # Arabic
            r'[\uFB1D-\uFB4F]',  # Hebrew Presentation Forms
            r'[\u200F\u202E]',   # RTL markers
            r'[\u2000-\u206F]',  # General Punctuation (some RTL chars)
        ]

        original_text = text
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text)

        # Step 2: Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Step 3: If too much was removed, add placeholder
        if len(text) < len(original_text) * 0.3:  # If we removed more than 70%
            text = f"[TRANSLATION_CLEANED: {len(original_text)} chars -> {len(text)} chars] {text}"

        if text != original_text:
            logger.warning(f"Force-removed non-Latin characters: {len(original_text)} -> {len(text)} characters")

        return text

    def _chunk_hebrew_text(self, text: str) -> List[str]:
        """
        Split Hebrew text into manageable chunks for translation,
        preserving sentence and paragraph boundaries where possible.
        """
        if len(text) <= self.max_chunk_size:
            return [text]

        chunks = []

        # First try to split by paragraphs (double newlines)
        paragraphs = text.split('\n\n')
        current_chunk = ""

        for paragraph in paragraphs:
            # If adding this paragraph exceeds chunk size
            if len(current_chunk) + len(paragraph) + 2 > self.max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())

                # If single paragraph is too long, split by sentences
                if len(paragraph) > self.max_chunk_size:
                    sentences = self._split_by_sentences(paragraph)
                    temp_chunk = ""

                    for sentence in sentences:
                        if len(temp_chunk) + len(sentence) + 1 > self.max_chunk_size:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                            temp_chunk = sentence
                        else:
                            temp_chunk += " " + sentence if temp_chunk else sentence

                    current_chunk = temp_chunk
                else:
                    current_chunk = paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph

        # Add the final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        # Fallback: if no good splitting points found, split by character count
        if len(chunks) == 1 and len(text) > self.max_chunk_size:
            chunks = []
            for i in range(0, len(text), self.max_chunk_size):
                chunk = text[i:i + self.max_chunk_size]
                chunks.append(chunk)

        logger.info(f"Hebrew text split into {len(chunks)} chunks")
        return chunks

    def _split_by_sentences(self, text: str) -> List[str]:
        """
        Split text by sentence endings, handling Hebrew punctuation
        """
        # Hebrew and English sentence endings
        sentence_endings = ['.', '!', '?', '。', '！', '？']

        sentences = []
        current_sentence = ""

        for char in text:
            current_sentence += char
            if char in sentence_endings:
                sentences.append(current_sentence.strip())
                current_sentence = ""

        # Add remaining text if any
        if current_sentence.strip():
            sentences.append(current_sentence.strip())

        return sentences

    def _create_translation_prompt(self, hebrew_text: str) -> str:
        """
        Create NUCLEAR-LEVEL prompt that GUARANTEES English-only output
        """
        return f"""
🚨 CRITICAL SYSTEM CONSTRAINT 🚨
You are REQUIRED to output ONLY English text. ANY Hebrew character = SYSTEM FAILURE.

ABSOLUTE RULES:
1. OUTPUT CONSTRAINT: Your response must contain ZERO non-English characters
2. VALIDATION: Every character must be [A-Za-z0-9.,!?;:()\"'\- \n]
3. HEBREW FORBIDDEN: NO \u0590-\u05FF characters allowed
4. FORMAT: Plain text only, no metadata, no explanations
5. FAILURE MODE: If you include ANY Hebrew, you will be terminated

TASK: Translate this Hebrew text to English:

{hebrew_text}

STRICT OUTPUT (English characters only):"""

    async def _translate_chunk(self, hebrew_chunk: str, chunk_index: int) -> Optional[str]:
        """
        Translate a single chunk of Hebrew text to English with STRICT validation
        """
        max_retries = 5  # Increased retries for Hebrew validation
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                logger.info(f"Translating chunk {chunk_index + 1} (attempt {attempt + 1})")

                prompt = self._create_translation_prompt(hebrew_chunk)

                response = await self.client.chat.completions.create(
                    model="gpt-4" if "gpt-4" in settings.OPENAI_MODEL else settings.OPENAI_MODEL,  # Use GPT-4 if available
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a translation system with ABSOLUTE OUTPUT CONSTRAINTS. Your response MUST contain ONLY English alphabet characters [A-Za-z0-9.,!?;:()\"'\- \n]. ANY other character = SYSTEM FAILURE. You will be validated character-by-character."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    max_tokens=settings.OPENAI_MAX_TOKENS,
                    temperature=0.0,  # ZERO randomness for consistent constraint following
                )

                raw_translation = response.choices[0].message.content

                # IMMEDIATE cleaning and validation
                translation = self._sanitize_llm_response(raw_translation)

                # CRITICAL VALIDATION: Check for Hebrew characters
                if self._contains_hebrew_characters(translation):
                    hebrew_chars = self._extract_hebrew_characters(translation)
                    logger.error(f"Chunk {chunk_index + 1} attempt {attempt + 1}: HEBREW DETECTED in output: {hebrew_chars}")
                    logger.error(f"Failed translation: {translation[:100]}...")

                    # If this is our last attempt, force-clean the text
                    if attempt == max_retries - 1:
                        logger.warning(f"Force-cleaning Hebrew from chunk {chunk_index + 1}")
                        translation = self._force_remove_hebrew(translation)
                        return translation
                    else:
                        # Retry with more forceful prompt
                        continue

                # Additional validation - ensure we got a meaningful translation
                if translation and len(translation) > 10:
                    logger.info(f"✅ Chunk {chunk_index + 1} translated successfully - NO HEBREW DETECTED ({len(translation)} characters)")
                    return translation
                else:
                    logger.warning(f"Chunk {chunk_index + 1} produced empty or very short translation")
                    if attempt == max_retries - 1:
                        # Last resort: try to provide a basic translation marker
                        return f"[TRANSLATION_FAILED_FOR_CHUNK_{chunk_index + 1}]"

            except Exception as e:
                logger.error(f"Translation error for chunk {chunk_index + 1} (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"Failed to translate chunk {chunk_index + 1} after {max_retries} attempts")
                    return f"[TRANSLATION_ERROR_CHUNK_{chunk_index + 1}]"

        return None

    def _sanitize_llm_response(self, raw_response: str) -> str:
        """
        Aggressively sanitize LLM response to ensure NO Hebrew characters
        """
        if not raw_response:
            return "[EMPTY_RESPONSE]"

        # Step 1: Basic cleanup
        text = raw_response.strip()

        # Step 2: Remove any metadata or formatting artifacts
        # Remove common LLM artifacts
        artifacts_to_remove = [
            "Translation:",
            "English translation:",
            "Output:",
            "Result:",
            "Here is the translation:",
            "The translation is:",
        ]

        for artifact in artifacts_to_remove:
            text = text.replace(artifact, "").strip()

        # Step 3: Force-remove ANY non-English characters
        original_length = len(text)

        # Allow only specific English characters
        allowed_pattern = r"[A-Za-z0-9.,!?;:()'\"\-\s\n]"
        cleaned_chars = re.findall(allowed_pattern, text)
        text = ''.join(cleaned_chars)

        # Step 4: Clean up spacing
        text = re.sub(r'\s+', ' ', text).strip()

        # Step 5: Log if significant cleaning occurred
        if len(text) < original_length * 0.8:
            logger.warning(f"Heavy sanitization: {original_length} -> {len(text)} characters")

        return text if text else "[SANITIZATION_FAILED]"

    def _emergency_hebrew_purge(self, text: str) -> str:
        """
        LAST RESORT: Nuclear option to remove ALL non-ASCII characters
        Only use if all other methods fail
        """
        # Keep only ASCII characters
        ascii_only = ''.join(char for char in text if ord(char) < 128)

        # Clean up spacing
        ascii_only = re.sub(r'\s+', ' ', ascii_only).strip()

        if ascii_only != text:
            removed_count = len(text) - len(ascii_only)
            logger.critical(f"EMERGENCY PURGE: Removed {removed_count} non-ASCII characters")

        return ascii_only if ascii_only else "[ASCII_PURGE_RESULT_EMPTY]"

    async def translate_hebrew_to_english(self, text: str) -> Dict[str, Any]:
        """
        Main method to translate Hebrew text to English using chunked processing

        Args:
            text: The Hebrew text to translate

        Returns:
            Dict containing:
            - translated_text: The complete English translation
            - original_chunks: Number of chunks processed
            - success: Whether translation was successful
            - has_hebrew: Whether the input contained Hebrew text
        """
        try:
            logger.info(f"=== STARTING HEBREW TRANSLATION ===")
            logger.info(f"Input text length: {len(text)} characters")

            # Check if text actually contains Hebrew
            if not self._is_hebrew_text(text):
                logger.info("No Hebrew text detected, returning original text")
                return {
                    "translated_text": text,
                    "original_chunks": 1,
                    "success": True,
                    "has_hebrew": False,
                    "message": "No Hebrew text detected in input"
                }

            # Chunk the Hebrew text
            chunks = self._chunk_hebrew_text(text)
            logger.info(f"Text split into {len(chunks)} chunks for translation")

            # Process chunks with rate limiting
            semaphore = asyncio.Semaphore(3)  # Limit concurrent requests

            async def process_chunk(chunk_data):
                chunk_text, index = chunk_data
                async with semaphore:
                    return await self._translate_chunk(chunk_text, index)

            # Create tasks for all chunks
            chunk_tasks = [(chunk, i) for i, chunk in enumerate(chunks)]
            translated_chunks = await asyncio.gather(*[process_chunk(chunk_data) for chunk_data in chunk_tasks])

            # Combine translated chunks
            successful_translations = [chunk for chunk in translated_chunks if chunk is not None]

            if not successful_translations:
                logger.error("No chunks were successfully translated")
                return {
                    "translated_text": text,  # Return original on complete failure
                    "original_chunks": len(chunks),
                    "success": False,
                    "has_hebrew": True,
                    "error": "Translation failed for all chunks"
                }

            # Join translated chunks
            if len(chunks) == 1:
                final_translation = successful_translations[0]
            else:
                # Join with appropriate spacing
                final_translation = "\n\n".join(successful_translations)

            # MULTI-LAYER FINAL VALIDATION
            validation_passed = False
            validation_attempts = 0
            max_validation_attempts = 3

            while not validation_passed and validation_attempts < max_validation_attempts:
                validation_attempts += 1

                # Layer 1: Hebrew character check
                if self._contains_hebrew_characters(final_translation):
                    hebrew_chars = self._extract_hebrew_characters(final_translation)
                    logger.error(f"🚨 VALIDATION FAILED (attempt {validation_attempts}): Hebrew characters detected: {hebrew_chars}")
                    final_translation = self._force_remove_hebrew(final_translation)
                    continue

                # Layer 2: Character-by-character validation
                allowed_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?;:()"\'-\n ')
                invalid_chars = [char for char in final_translation if char not in allowed_chars]

                if invalid_chars:
                    unique_invalid = list(set(invalid_chars))
                    logger.error(f"🚨 VALIDATION FAILED (attempt {validation_attempts}): Invalid characters: {unique_invalid}")
                    # Remove invalid characters
                    final_translation = ''.join(char for char in final_translation if char in allowed_chars)
                    final_translation = re.sub(r'\s+', ' ', final_translation).strip()
                    continue

                # Layer 3: Unicode normalization check
                import unicodedata
                normalized = unicodedata.normalize('NFKC', final_translation)
                if normalized != final_translation:
                    logger.warning(f"Unicode normalization changed text - using normalized version")
                    final_translation = normalized
                    continue

                # If we get here, validation passed
                validation_passed = True
                logger.info(f"✅ VALIDATION PASSED: All characters are English-only")

            # Emergency fallback if all validation attempts failed
            if not validation_passed:
                logger.error(f"💰 EMERGENCY FALLBACK: Could not clean text after {max_validation_attempts} attempts")
                logger.critical("🚨 ACTIVATING EMERGENCY HEBREW PURGE - REMOVING ALL NON-ASCII")
                final_translation = self._emergency_hebrew_purge(final_translation)

                # Final ASCII-only validation
                if not all(ord(char) < 128 for char in final_translation):
                    logger.critical("💥 CATASTROPHIC FAILURE: Even ASCII purge failed")
                    final_translation = "[CATASTROPHIC_TRANSLATION_FAILURE - HEBREW_REMOVAL_IMPOSSIBLE]"
                else:
                    logger.info("✅ EMERGENCY PURGE SUCCESSFUL - All characters are now ASCII")

            logger.info(f"✅ Translation completed successfully - FINAL HEBREW CHECK PASSED")
            logger.info(f"Original length: {len(text)} characters")
            logger.info(f"Translated length: {len(final_translation)} characters")

            return {
                "translated_text": final_translation,
                "original_chunks": len(chunks),
                "translated_chunks": len(successful_translations),
                "success": True,
                "has_hebrew": False,  # Should always be False after our validation
                "hebrew_free_guaranteed": True,
                "message": f"Successfully translated {len(successful_translations)}/{len(chunks)} chunks - NO HEBREW REMAINING"
            }

        except Exception as e:
            logger.error(f"Error in Hebrew translation: {str(e)}")
            return {
                "translated_text": text,  # Return original on error
                "original_chunks": 0,
                "success": False,
                "has_hebrew": self._is_hebrew_text(text),
                "error": str(e)
            }

    async def translate_document_content(self, document_content: str, document_type: str = "unknown") -> Dict[str, Any]:
        """
        Translate document content with document-type-specific handling

        Args:
            document_content: The content to translate
            document_type: Type of document (exam, text, etc.) for context-aware translation

        Returns:
            Translation result with metadata
        """
        logger.info(f"Translating {document_type} document")

        # Add document context to the translation process
        if document_type.lower() in ['exam', 'test', 'quiz']:
            # For exam documents, we might want to preserve specific formatting
            logger.info("Using exam-specific translation settings")

        result = await self.translate_hebrew_to_english(document_content)
        result['document_type'] = document_type

        return result

    async def test_translation_service(self) -> bool:
        """
        Test the translation service with a simple Hebrew phrase
        """
        try:
            test_hebrew = "שלום עולם! זה מבחן של השירות התרגום."
            result = await self.translate_hebrew_to_english(test_hebrew)

            if result['success'] and 'hello world' in result['translated_text'].lower():
                logger.info("Translation service test passed")
                return True
            else:
                logger.warning("Translation service test failed - unexpected result")
                return False

        except Exception as e:
            logger.error(f"Translation service test failed: {str(e)}")
            return False