import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
import re
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.max_chunk_size = 3000  # Conservative chunk size for GPT-3.5-turbo
        
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text to remove common instruction patterns that aren't questions
        Enhanced for cybersecurity exams
        """
        # Remove common instruction headers and footers
        instruction_patterns = [
            r'^.*?(תקנון|הוראות|הנחיות|ביאור|רקע|הורמאות).*?\n',  # Hebrew instructions
            r'^.*?(Instructions|Directions|Guidelines|Background|Note).*?\n',  # English instructions
            r'^\s*שם\s*המועמד.*?\n',  # Hebrew name fields
            r'^\s*(Name|Student|ID).*?:.*?\n',  # English name/ID fields
            r'^\s*מספר\s*תעודת\s*זהות.*?\n',  # Hebrew ID number
            r'^\s*תאריך.*?\n',  # Hebrew date
            r'^\s*(Date|Time|Duration).*?:.*?\n',  # English date/time
            r'^\s*זמן\s*המבחן.*?\n',  # Hebrew exam time
            r'^\s*ציון.*?\n',  # Hebrew grade
            r'^\s*(Score|Grade|Points).*?:.*?\n',  # English score
            r'^\s*חתימת\s*הבוחן.*?\n',  # Hebrew examiner signature
            r'^\s*(Signature|Examiner).*?\n',  # English signature
            r'^\s*דף\s*\d+\s*מתוך\s*\d+.*?\n',  # Hebrew page numbers
            r'^\s*Page\s*\d+\s*of\s*\d+.*?\n',  # English page numbers
            
            # Cybersecurity exam specific patterns
            r'^.*?(Cybersecurity\s+Exam|Security\s+Test|מבחן\s+אבטחה).*?\n',  # Exam titles
            r'^.*?(Part\s+[A-Z]|חלק\s+[א-ז]).*?\n',  # Section headers
            r'^.*?(Total\s+Questions|סך\s+השאלות).*?\n',  # Question count headers
            r'^.*?בהצלחה.*?\n',  # Hebrew "good luck"
        ]
        
        for pattern in instruction_patterns:
            text = re.sub(pattern, '', text, flags=re.MULTILINE | re.IGNORECASE)
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Multiple blank lines
        text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)  # Leading whitespace
        
        logger.info(f"Preprocessed text length: {len(text)} characters")
        return text
    
    def _chunk_text_intelligently(self, text: str) -> List[str]:
        """
        Split text into chunks intelligently, preserving question boundaries
        Enhanced for cybersecurity multiple choice questions
        """
        # First preprocess to remove instruction text
        text = self._preprocess_text(text)
        
        chunks = []
        
        # Enhanced question patterns for Hebrew, English, and cybersecurity tests
        question_patterns = [
            # Standard numbered patterns
            r'(?=(?:\n|^)\s*(?:\d+)[\.\)]\s*)',  # 1. 2. 3.
            r'(?=(?:\n|^)\s*(?:שאלה\s*\d+)[\.\):]\s*)',  # Hebrew question numbers
            r'(?=(?:\n|^)\s*(?:Question\s*\d+)[\.\):]\s*)',  # English question numbers
            r'(?=(?:\n|^)\s*(?:Q\d+)[\.\):]\s*)',  # Q1, Q2, etc.
            r'(?=(?:\n|^)\s*(?:\(\d+\))\s*)',  # (1) (2) (3)
            r'(?=(?:\n|^)\s*(?:\d+\s*[\-\–\—])\s*)',  # 1- 2- 3- with various dashes
            
            # Cybersecurity specific patterns
            r'(?=(?:\n|^)\s*(?:\d+\s*\.)\s*(?:What|Which|How|When|Where|Why|If|A\s+security|The\s+best|An\s+attacker))',  # English cyber questions
            r'(?=(?:\n|^)\s*(?:\d+\s*[\.\)])\s*(?:מה|איך|מתי|איפה|למה|כיצד|האם|מערכת\s+אבטחה|תוקף))',  # Hebrew cyber questions
        ]
        
        # Try each pattern and use the one that gives best segmentation
        best_segments = None
        best_count = 0
        
        for pattern in question_patterns:
            try:
                segments = re.split(pattern, text)
                valid_segments = [s.strip() for s in segments if s.strip() and len(s.strip()) > 15]
                
                if len(valid_segments) > best_count:
                    best_count = len(valid_segments)
                    best_segments = valid_segments
            except re.error:
                continue
        
        # Enhanced fallback for cybersecurity tests - more aggressive
        if not best_segments or best_count < 10:  # Changed from 8 to 10 - we expect exactly 10 questions
            # Try splitting by lines that start with numbers - be very aggressive
            lines = text.split('\n')
            segments = []
            current_segment = ""
            
            logger.info(f"Fallback mode: Processing {len(lines)} lines for numbered questions")
            
            for i, line in enumerate(lines):
                line = line.strip()
                # Check if this line starts a new question - be very permissive
                if re.match(r'^\d+[\.\)\-\s]+', line) and len(line) > 3:  # Any number followed by punctuation
                    if current_segment:
                        segments.append(current_segment.strip())
                        logger.info(f"Found potential question segment: {current_segment.strip()[:50]}...")
                    current_segment = line
                elif current_segment:  # We're in a question, add this line to it
                    current_segment += "\n" + line
            
            if current_segment:
                segments.append(current_segment.strip())
                logger.info(f"Found final question segment: {current_segment.strip()[:50]}...")
            
            logger.info(f"Fallback found {len(segments)} potential question segments")
            
            # Be less strict with cybersecurity filtering - use general question validation
            valid_segments = [s for s in segments if len(s.strip()) > 20]  # Just check length
            
            if len(valid_segments) > best_count:
                best_segments = valid_segments
                logger.info(f"Using fallback segments: {len(valid_segments)} questions")
        
        if not best_segments:
            # Final fallback: split by double newlines and filter
            potential_questions = [s.strip() for s in text.split('\n\n') if s.strip()]
            best_segments = [s for s in potential_questions if self._looks_like_question_content(s)]
        
        current_chunk = ""
        
        for segment in best_segments:
            # If adding this segment would exceed chunk size, start a new chunk
            if len(current_chunk) + len(segment) > self.max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = segment
            else:
                current_chunk += "\n\n" + segment if current_chunk else segment
        
        # Add the final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If no intelligent splitting worked, fall back to simple chunking
        if len(chunks) == 1 and len(text) > self.max_chunk_size:
            chunks = []
            for i in range(0, len(text), self.max_chunk_size):
                chunk = text[i:i + self.max_chunk_size]
                chunks.append(chunk)
        
        logger.info(f"Text split into {len(chunks)} chunks after preprocessing (found {len(best_segments) if best_segments else 0} potential questions)")
        return chunks
    
    def _extract_numbered_questions_deterministic(self, text: str) -> List[Dict[str, Any]]:
        """
        DETERMINISTIC: Extract numbered questions (1., 2., 3., etc.) with high confidence
        This provides a baseline count of expected questions for validation
        """
        questions = []
        
        # Clean text but preserve structure
        lines = text.split('\n')
        current_question = ""
        current_number = 0
        
        logger.info(f"DETERMINISTIC SCAN: Processing {len(lines)} lines")
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check if this line starts a new numbered question
            number_match = re.match(r'^(\d+)[\.\)]\s*(.*)', line)
            
            if number_match:
                # Save previous question if exists
                if current_question and current_number > 0:
                    questions.append({
                        'number': current_number,
                        'text': current_question.strip(),
                        'raw_text': current_question,
                        'line_start': i - current_question.count('\n'),
                        'line_end': i - 1
                    })
                    logger.info(f"  FOUND Q{current_number}: {current_question[:50]}...")
                
                # Start new question
                current_number = int(number_match.group(1))
                current_question = line
                
            elif current_question and current_number > 0:
                # Continue building current question
                current_question += "\n" + line
        
        # Don't forget the last question
        if current_question and current_number > 0:
            questions.append({
                'number': current_number,
                'text': current_question.strip(),
                'raw_text': current_question,
                'line_start': len(lines) - current_question.count('\n'),
                'line_end': len(lines) - 1
            })
            logger.info(f"  FOUND Q{current_number}: {current_question[:50]}...")
        
        # Validate sequence completeness for cybersecurity exam (expect 1-10)
        expected_numbers = set(range(1, 11))
        found_numbers = {q['number'] for q in questions}
        missing_numbers = expected_numbers - found_numbers
        extra_numbers = found_numbers - expected_numbers
        
        logger.info(f"SEQUENCE ANALYSIS:")
        logger.info(f"  Expected: 1-10 (cybersecurity exam)")
        logger.info(f"  Found: {sorted(found_numbers)}")
        logger.info(f"  Missing: {sorted(missing_numbers) if missing_numbers else 'None'}")
        logger.info(f"  Extra: {sorted(extra_numbers) if extra_numbers else 'None'}")
        
        return questions
    
    def _recover_missing_questions(self, text: str, deterministic_questions: List[Dict], 
                                 found_questions: List[Dict]) -> List[Dict[str, Any]]:
        """
        RECOVERY MODE: Use deterministic scan to find questions LLM missed
        """
        logger.info("=== RECOVERY MODE ACTIVATED ===")
        
        # Get question numbers we found via LLM
        found_numbers = set()
        for q in found_questions:
            # Try to extract question number from text
            question_text = q.get('question_text', '')
            number_match = re.match(r'^(\d+)[\.\)]\s*', question_text.strip())
            if number_match:
                found_numbers.add(int(number_match.group(1)))
        
        # Find missing questions from deterministic scan
        missing_questions = []
        for det_q in deterministic_questions:
            if det_q['number'] not in found_numbers:
                logger.info(f"RECOVERING Q{det_q['number']}: {det_q['text'][:100]}...")
                
                # Create question object in expected format
                recovered_question = {
                    'question_id': f"recovery_q_{det_q['number']}",
                    'question_text': det_q['text'],
                    'question_type': self._determine_question_type_simple(det_q['text']),
                    'topic': 'Cybersecurity',
                    'difficulty': 'medium',
                    'confidence_score': 0.8,  # High confidence from deterministic detection
                    'source_chunk': 'recovery',
                    'detection_method': 'deterministic_recovery',
                    'question_number': det_q['number']
                }
                
                # Basic validation - just check it's not empty and has reasonable content
                if len(det_q['text'].strip()) > 20:
                    missing_questions.append(recovered_question)
                    logger.info(f"  ✓ RECOVERED Q{det_q['number']}")
                else:
                    logger.info(f"  ✗ SKIPPED Q{det_q['number']} - Too short")
        
        logger.info(f"RECOVERY RESULT: {len(missing_questions)} questions recovered")
        return missing_questions
    
    def _determine_question_type_simple(self, question_text: str) -> str:
        """Simple question type detection for recovery mode"""
        text_lower = question_text.lower()
        
        # Multiple choice indicators
        if any(indicator in question_text for indicator in ['a)', 'b)', 'c)', 'd)', 'A)', 'B)', 'C)', 'D)']):
            return "multiple_choice"
        
        # True/false indicators
        if any(indicator in text_lower for indicator in ['true or false', 'true/false', 't/f']):
            return "true_false"
        
        return "multiple_choice"  # Default for cybersecurity exams
    
    def _validate_against_deterministic_scan(self, final_questions: List[Dict], 
                                           deterministic_questions: List[Dict]):
        """
        QUALITY CONTROL: Compare final results against deterministic baseline
        """
        logger.info("=== QUALITY CONTROL VALIDATION ===")
        
        det_numbers = {q['number'] for q in deterministic_questions}
        found_numbers = set()
        
        for q in final_questions:
            question_text = q.get('question_text', '')
            number_match = re.match(r'^(\d+)[\.\)]\s*', question_text.strip())
            if number_match:
                found_numbers.add(int(number_match.group(1)))
        
        expected_range = set(range(1, 11))  # 1-10 for cybersecurity exams
        
        logger.info(f"DETERMINISTIC BASELINE: {len(det_numbers)} questions - {sorted(det_numbers)}")
        logger.info(f"FINAL DETECTION: {len(found_numbers)} questions - {sorted(found_numbers)}")
        logger.info(f"EXPECTED RANGE: {sorted(expected_range)}")
        
        missing_from_expected = expected_range - found_numbers
        extra_beyond_expected = found_numbers - expected_range
        
        if missing_from_expected:
            logger.warning(f"MISSING QUESTIONS: {sorted(missing_from_expected)}")
        if extra_beyond_expected:
            logger.warning(f"EXTRA QUESTIONS: {sorted(extra_beyond_expected)}")
        
        # Coverage analysis
        coverage = len(found_numbers & expected_range) / len(expected_range)
        logger.info(f"DETECTION COVERAGE: {coverage:.2%} (expected 100%)")
        
        if coverage < 0.9:  # Less than 90% coverage is concerning
            logger.error(f"LOW COVERAGE ALERT: Only {coverage:.2%} of expected questions detected!")
        elif coverage == 1.0:
            logger.info("✓ PERFECT COVERAGE: All expected questions detected!")
    
    def _looks_like_question_content(self, text: str) -> bool:
        """
        Determine if a text segment likely contains question content
        """
        text_lower = text.lower()
        
        # Must contain question indicators
        question_indicators = ['?', 'מה', 'איך', 'מתי', 'איפה', 'למה', 'כמה', 'what', 'how', 'when', 'where', 'why', 'which', 'who']
        has_question_indicator = any(indicator in text_lower for indicator in question_indicators)
        
        # Must have reasonable length (not just a title)
        has_reasonable_length = len(text.strip()) > 15
        
        # Should not be instruction text
        instruction_keywords = [
            'הוראות', 'הנחיות', 'תקנון', 'שם המועמד', 'תעודת זהות', 'זמן המבחן',
            'instructions', 'directions', 'guidelines', 'name:', 'id:', 'student:', 'time:', 'duration:'
        ]
        is_not_instruction = not any(keyword in text_lower for keyword in instruction_keywords)
        
        return has_question_indicator and has_reasonable_length and is_not_instruction
    
    def _looks_like_cybersecurity_question(self, text: str) -> bool:
        """
        Enhanced validation specifically for cybersecurity multiple choice questions
        """
        text_lower = text.lower()
        
        # Must have reasonable length
        if len(text.strip()) < 20:
            return False
        
        # Check for cybersecurity-specific terms
        cyber_terms = [
            # English cybersecurity terms
            'security', 'attack', 'vulnerability', 'encryption', 'malware', 'firewall',
            'authentication', 'authorization', 'password', 'network', 'protocol',
            'threat', 'risk', 'breach', 'intrusion', 'phishing', 'virus', 'trojan',
            'ssl', 'tls', 'vpn', 'dos', 'ddos', 'sql injection', 'xss', 'csrf',
            'penetration', 'audit', 'compliance', 'cipher', 'hash', 'digital signature',
            
            # Hebrew cybersecurity terms  
            'אבטחה', 'התקפה', 'פרצה', 'הצפנה', 'תוכנה זדונית', 'חומת אש',
            'אימות', 'הרשאה', 'סיסמה', 'רשת', 'פרוטוקול', 'איום', 'סיכון',
            'פריצה', 'חדירה', 'דיוג', 'וירוס', 'טרויאני'
        ]
        
        has_cyber_content = any(term in text_lower for term in cyber_terms)
        
        # Check for question indicators
        question_indicators = [
            '?', 'מה', 'איך', 'מתי', 'איפה', 'למה', 'כמה', 'האם', 'מדוע',
            'what', 'how', 'when', 'where', 'why', 'which', 'who', 'is', 'are',
            'can', 'will', 'should', 'does', 'do'
        ]
        
        has_question_indicator = any(indicator in text_lower for indicator in question_indicators)
        
        # Check for multiple choice indicators
        mc_indicators = [
            'א)', 'ב)', 'ג)', 'ד)', 'A)', 'B)', 'C)', 'D)',
            '1)', '2)', '3)', '4)', '(א)', '(ב)', '(ג)', '(ד)',
            '(A)', '(B)', '(C)', '(D)', '(1)', '(2)', '(3)', '(4)',
            'a.', 'b.', 'c.', 'd.', '1.', '2.', '3.', '4.'
        ]
        
        has_multiple_choice = any(indicator in text for indicator in mc_indicators)
        
        # Check for numbered question start
        starts_with_number = re.match(r'^\d+[\.\)]\s*', text.strip())
        
        # Should not be instruction text
        instruction_keywords = [
            'הוראות', 'הנחיות', 'תקנון', 'שם המועמד', 'תעודת זהות', 'זמן המבחן',
            'instructions', 'directions', 'guidelines', 'name:', 'id:', 'student:', 'time:', 'duration:',
            'exam instructions', 'test instructions'
        ]
        is_not_instruction = not any(keyword in text_lower for keyword in instruction_keywords)
        
        # Enhanced scoring for cybersecurity questions
        score = 0
        if has_cyber_content: score += 3  # Strong indicator for cybersecurity domain
        if has_question_indicator: score += 2
        if has_multiple_choice: score += 2  # Strong indicator for multiple choice
        if starts_with_number: score += 1
        if is_not_instruction: score += 1
        if len(text.strip()) > 50: score += 1  # Reasonable length for a full question
        
        # More permissive for questions that start with numbers (likely questions)
        if starts_with_number and has_question_indicator and len(text.strip()) > 30:
            score += 2  # Boost for numbered questions
        
        # Debug logging
        logger.info(f"Question validation - Text: {text[:50]}...")
        logger.info(f"  Scores: cyber={3 if has_cyber_content else 0}, question={2 if has_question_indicator else 0}, mc={2 if has_multiple_choice else 0}, numbered={1 if starts_with_number else 0}, not_inst={1 if is_not_instruction else 0}, length={1 if len(text.strip()) > 50 else 0}")
        logger.info(f"  Total score: {score}, Threshold: 1 (was 2, originally 4)")
        
        return score >= 1  # Ultra-permissive threshold for maximum detection (was 2, originally 4)
    
    def _validate_question(self, question: Dict[str, Any]) -> bool:
        """
        Validate that a question is actually a genuine exam question
        """
        question_text = question.get('question_text', '').strip()
        
        if not question_text or len(question_text) < 10:
            return False
        
        text_lower = question_text.lower()
        
        # Reject obvious non-questions
        reject_patterns = [
            # Hebrew patterns
            r'^.*?(שם|תעודת זהות|מספר|תאריך|זמן|ציון|חתימה).*?:',
            r'^.*?(הוראות|הנחיות|תקנון|ביאור|רקע)',
            r'^.*?דף\s*\d+\s*מתוך\s*\d+',
            r'^.*?בהצלחה|בהצלחה.*?$',
            r'^.*?מועד\s*[אב].*?$',
            
            # English patterns
            r'^.*?(name|student|id|date|time|score|signature).*?:',
            r'^.*?(instructions|directions|guidelines|background|note)',
            r'^.*?page\s*\d+\s*of\s*\d+',
            r'^.*?good\s*luck',
            r'^.*?(exam|test)\s*(name|title)',
            
            # Generic patterns
            r'^\s*[־\-_=]{3,}',  # Lines/dividers
            r'^\s*\d+\s*$',      # Just numbers
            r'^\s*[א-ת\s]{1,3}\s*$',  # Very short Hebrew text
            r'^\s*[a-zA-Z\s]{1,3}\s*$',  # Very short English text
        ]
        
        for pattern in reject_patterns:
            if re.match(pattern, text_lower, re.MULTILINE | re.IGNORECASE):
                return False
        
        # Must have question indicators
        question_indicators = ['?', 'מה', 'איך', 'מתי', 'איפה', 'למה', 'כמה', 'האם', 'מדוע', 'כיצד',
                             'what', 'how', 'when', 'where', 'why', 'which', 'who', 'explain', 'describe',
                             'calculate', 'solve', 'find', 'determine', 'identify', 'analyze', 'compare']
        
        has_question_indicator = any(indicator in text_lower for indicator in question_indicators)
        
        # Check if it has multiple choice options (strong indicator of a real question)
        has_options = any(pattern in question_text for pattern in [
            'א)', 'ב)', 'ג)', 'ד)', 'A)', 'B)', 'C)', 'D)',
            '1)', '2)', '3)', '4)', '(א)', '(ב)', '(ג)', '(ד)',
            '(A)', '(B)', '(C)', '(D)', '(1)', '(2)', '(3)', '(4)'
        ])
        
        # Must have either question indicator or multiple choice options
        if not (has_question_indicator or has_options):
            return False
        
        # Check confidence score - EXTREMELY permissive (almost disabled)
        confidence = question.get('confidence_score', 0.5)
        if confidence < 0.01:  # Only reject if virtually zero confidence
            logger.info(f"  ✗ REJECTED: Extremely low confidence ({confidence})")
            return False
        
        # Additional validation for question structure - more permissive
        if question.get('question_type') == 'unknown' and not has_options and '?' not in question_text:
            # Check if it starts with a number (likely a question even without explicit indicators)
            if not re.match(r'^\d+[\.\)]\s*', question_text.strip()):
                return False
        
        # Debug logging for validation
        logger.info(f"Final validation - Question: {question_text[:50]}...")
        logger.info(f"  Has question indicator: {has_question_indicator}")
        logger.info(f"  Has options: {has_options}")
        logger.info(f"  Question type: {question.get('question_type')}")
        logger.info(f"  Confidence: {confidence}")
        logger.info(f"  Result: PASSED")
        
        return True
    
    def _create_analysis_prompt(self, text_chunk: str) -> str:
        """
        Create a structured prompt for question analysis
        Enhanced for cybersecurity multiple choice questions
        """
        return f"""
You are an expert educational content analyzer specializing in cybersecurity and IT security exams. Your job is to identify ONLY actual exam questions, NOT instructions, headers, titles, or administrative text.

MANDATORY TRANSLATION REQUIREMENT:
- TRANSLATE EVERY SINGLE WORD of Hebrew/non-English content to English
- NEVER leave any Hebrew text untranslated - convert 100% to English
- TRANSLATE the complete question text, ALL answer options, and any explanatory text
- Convert Hebrew multiple choice indicators (א,ב,ג,ד) to (A,B,C,D)
- Maintain technical accuracy while translating cybersecurity terminology
- Keep the original structure and numbering but convert ALL text content to professional English

Text to analyze:
{text_chunk}

DOMAIN FOCUS: This appears to be a CYBERSECURITY/IT SECURITY exam. Pay special attention to:
- Security concepts, threats, vulnerabilities, attacks
- Network security, encryption, authentication protocols
- Multiple choice questions with technical cybersecurity content
- Questions starting with numbers (1., 2., 3., etc.)

CRITICAL: Extract ONLY genuine exam questions that students need to answer. IGNORE:
- Instructions and directions (הוראות, הנחיות, Instructions, Directions)
- Header information (names, dates, exam titles, page numbers)
- Administrative text (student name fields, ID numbers, signatures)
- Section titles and headings ("Cybersecurity Exam", "Part A", etc.)
- Answer sheet instructions
- Time limits and grading information

A valid CYBERSECURITY question MUST:
1. Ask something specific about security, threats, protocols, or IT concepts
2. Be numbered (1., 2., 3., etc.) and have substantive content
3. Include multiple choice options (A, B, C, D or א, ב, ג, ד)
4. Have sufficient technical content (more than just a title or heading)
5. Contain cybersecurity-related terms (security, attack, encryption, network, etc.)

ENHANCED DETECTION for 10-question cybersecurity exams:
- Look for patterns: "1. What is...", "2. Which of the following...", "3. How does..."
- Multiple choice questions typically have 4 options (A-D or א-ד)
- Questions often start with: What, Which, How, When, Why, If, The best way to...
- Pay attention to cybersecurity terminology in both Hebrew and English

Return ONLY a valid JSON object with this structure:
{{
    "questions": [
        {{
            "question_id": "q_{{number}}",
            "question_text": "complete question text in ENGLISH including ALL answer options translated to English",
            "question_type": "multiple_choice",
            "topic": "Cybersecurity",
            "difficulty": "easy|medium|hard",
            "confidence_score": 0.95,
            "answer_choices": ["A) first option in English", "B) second option in English", "C) third option in English", "D) fourth option in English"],
            "keywords": ["security", "network", "encryption"],
            "is_valid_question": true
        }}
    ],
    "chunk_summary": {{
        "total_questions": 10,
        "primary_topics": ["Cybersecurity", "Network Security"],
        "question_types_found": ["multiple_choice"],
        "excluded_text_count": 0,
        "detection_confidence": "high"
    }}
}}

Question Classification for Cybersecurity:
- multiple_choice: Has A/B/C/D or א/ב/ג/ד options (most common in cybersecurity exams)
- true_false: Asks if security statement is true/false
- short_answer: Requires brief technical explanation
- essay: Requires extended security analysis

CRITICAL INSTRUCTIONS FOR 10/10 DETECTION:
1. MANDATORY: SCAN EVERY SINGLE LINE that starts with a number (1., 2., 3., etc.)
2. If a numbered line has ANY content (even 3+ words), it MUST be included as a question
3. NEVER exclude numbered items - include even general IT/computer/technology questions
4. For each numbered item, capture ALL text until the next numbered item starts
5. Be EXTREMELY permissive - include anything that looks like a test question
6. TARGET: Extract EXACTLY 10 questions (standard cybersecurity exam format)

MANDATORY QUALITY CONTROL:
- FIRST: Count all lines starting with "1.", "2.", "3.", etc. in the text
- SECOND: Your JSON output MUST have exactly that many questions
- THIRD: If your count doesn't match, re-examine every numbered line

ULTRA-AGGRESSIVE RECOVERY MODE:
If you find fewer than 10 questions on first pass:
1. Re-scan for ANY numbered patterns: "1)", "(1)", "1-", "1 ", etc.
2. Include partial questions, incomplete questions, anything numbered
3. Include technical questions even without cybersecurity terms
4. Include system, network, computer, software, hardware, data questions
5. GOAL: Achieve 10/10 detection rate at all costs

REMEMBER: This is a 10-question cybersecurity exam. The baseline expectation is 10 questions. Anything less than 10 indicates a detection failure that must be corrected.

CRITICAL FINAL TRANSLATION CHECK:
- ZERO Hebrew or non-English words allowed in the output
- Every single question_text must be 100% English - no mixed languages
- Every single answer_choice must be 100% English - no mixed languages
- Hebrew letters (א, ב, ג, ד) MUST be converted to English letters (A, B, C, D)
- Technical terms MUST use standard English cybersecurity terminology
- REJECT any output that contains untranslated Hebrew/foreign text
- If you see Hebrew characters in your JSON, you FAILED - translate them to English

Return only valid JSON, no additional text.
"""
    
    async def _call_openai_api(self, prompt: str, chunk_index: int) -> Optional[Dict[str, Any]]:
        """
        Make API call to OpenAI with error handling and retries
        """
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Analyzing chunk {chunk_index + 1} (attempt {attempt + 1})")
                
                response = await self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system", 
                            "content": "You are an expert educational content analyzer. Always return valid JSON."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=settings.OPENAI_MAX_TOKENS,
                    temperature=settings.OPENAI_TEMPERATURE,
                    response_format={"type": "json_object"}
                )
                
                content = response.choices[0].message.content
                
                # Parse JSON response
                try:
                    result = json.loads(content)
                    logger.info(f"Chunk {chunk_index + 1}: Found {len(result.get('questions', []))} questions")
                    return result
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error for chunk {chunk_index + 1}: {e}")
                    logger.error(f"Raw response: {content}")
                    
                    # Try to extract JSON from response if it's wrapped in text
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        try:
                            result = json.loads(json_match.group())
                            return result
                        except json.JSONDecodeError:
                            pass
                    
                    if attempt == max_retries - 1:
                        return None
                    
            except Exception as e:
                logger.error(f"API call error for chunk {chunk_index + 1} (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    return None
        
        return None
    
    async def analyze_text_with_llm(self, text: str) -> Dict[str, Any]:
        """
        Main method to analyze text using GPT-3.5-turbo with intelligent chunking
        Enhanced with deterministic question detection and detailed logging
        """
        try:
            logger.info(f"=== STARTING ENHANCED LLM ANALYSIS ===")
            logger.info(f"Input text length: {len(text)} characters")
            
            # PHASE 1: Pre-scan for numbered questions (deterministic)
            numbered_questions = self._extract_numbered_questions_deterministic(text)
            logger.info(f"PHASE 1 - Deterministic scan found {len(numbered_questions)} numbered questions")
            for i, q in enumerate(numbered_questions[:3]):  # Log first 3 for debugging
                logger.info(f"  Question {i+1}: {q['text'][:100]}...")
            
            # PHASE 2: Chunk the text intelligently
            chunks = self._chunk_text_intelligently(text)
            
            # Process chunks concurrently (but with rate limiting)
            semaphore = asyncio.Semaphore(3)  # Limit concurrent requests
            
            async def process_chunk(chunk_data):
                chunk_text, index = chunk_data
                async with semaphore:
                    prompt = self._create_analysis_prompt(chunk_text)
                    return await self._call_openai_api(prompt, index)
            
            # Create tasks for all chunks
            chunk_tasks = [(chunk, i) for i, chunk in enumerate(chunks)]
            results = await asyncio.gather(*[process_chunk(chunk_data) for chunk_data in chunk_tasks])
            
            # PHASE 3: Combine results with enhanced validation and recovery
            all_questions = []
            all_topics = set()
            question_types = set()
            excluded_questions = 0
            
            logger.info(f"PHASE 3 - Processing LLM results from {len(results)} chunks")
            
            for i, result in enumerate(results):
                if result and 'questions' in result:
                    chunk_questions = result['questions']
                    logger.info(f"Chunk {i+1}: Processing {len(chunk_questions)} questions")
                    
                    # Post-process each question for validation
                    for j, question in enumerate(chunk_questions):
                        logger.info(f"  Chunk {i+1} Q{j+1}: {question.get('question_text', 'Unknown')[:100]}...")
                        logger.info(f"    - Type: {question.get('question_type')}, Topic: {question.get('topic')}")
                        logger.info(f"    - Confidence: {question.get('confidence_score', 'Unknown')}")
                        
                        if self._validate_question(question):
                            question['question_id'] = f"chunk_{i+1}_{question.get('question_id', len(all_questions))}"
                            question['source_chunk'] = i + 1
                            question['detection_method'] = 'llm'
                            all_questions.append(question)
                            
                            # Collect topics and types
                            if question.get('topic'):
                                all_topics.add(question['topic'])
                            if question.get('question_type'):
                                question_types.add(question['question_type'])
                            logger.info(f"    ✓ ACCEPTED - Total questions: {len(all_questions)}")
                        else:
                            excluded_questions += 1
                            logger.info(f"    ✗ EXCLUDED - Failed validation")
                            logger.info(f"      Preview: {question.get('question_text', 'Unknown')[:100]}")
                
                else:
                    logger.warning(f"Chunk {i+1}: No valid LLM result")
            
            logger.info(f"PHASE 3 COMPLETE: {len(all_questions)} valid, {excluded_questions} excluded")
            
            # PHASE 4: Recovery logic if we don't have 10 questions
            if len(all_questions) < 10:
                logger.warning(f"RECOVERY MODE: Only {len(all_questions)}/10 questions found, triggating fallback")
                recovery_questions = self._recover_missing_questions(text, numbered_questions, all_questions)
                
                if recovery_questions:
                    logger.info(f"RECOVERY: Found {len(recovery_questions)} additional questions")
                    all_questions.extend(recovery_questions)
                    logger.info(f"RECOVERY COMPLETE: Total questions now {len(all_questions)}")
                else:
                    logger.warning(f"RECOVERY FAILED: No additional questions recovered")
            
            # PHASE 5: Final validation against deterministic scan
            self._validate_against_deterministic_scan(all_questions, numbered_questions)
            
            # Create topic summary
            topic_counts = {}
            for question in all_questions:
                topic = question.get('topic', 'Unknown')
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            topics = [
                {
                    "topic_id": f"topic_{i}",
                    "topic_name": topic,
                    "question_count": count,
                    "keywords": [topic.lower().replace(" ", "_")],
                    "confidence_score": 0.8
                }
                for i, (topic, count) in enumerate(topic_counts.items())
            ]
            
            # Create final result
            final_result = {
                "questions": all_questions,
                "topics": topics,
                "clusters": [],  # Could implement clustering later
                "summary": {
                    "total_questions": len(all_questions),
                    "topics_found": len(topics),
                    "question_types": list(question_types),
                    "chunks_processed": len(chunks),
                    "processing_success": True
                }
            }
            
            logger.info(f"LLM analysis completed: {len(all_questions)} questions, {len(topics)} topics")
            return final_result
            
        except Exception as e:
            logger.error(f"Error in LLM analysis: {str(e)}")
            return {
                "questions": [],
                "topics": [],
                "clusters": [],
                "summary": {
                    "total_questions": 0,
                    "topics_found": 0,
                    "processing_success": False,
                    "error": str(e)
                }
            }
    
    async def test_api_connection(self) -> bool:
        """
        Test the OpenAI API connection
        """
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"API connection test failed: {str(e)}")
            return False