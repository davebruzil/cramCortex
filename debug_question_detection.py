#!/usr/bin/env python3
"""
Enhanced Question Detection Debugging Script for cramCortex
Provides detailed logging and analysis of question detection pipeline
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.services.llm_question_analyzer import LLMQuestionAnalyzer

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('question_detection_debug.log')
    ]
)

logger = logging.getLogger(__name__)

# Sample cybersecurity test content for debugging
SAMPLE_CYBERSECURITY_TEST = """
Cybersecurity Final Exam
Student Name: _______________
ID: _______________
Date: December 2024

Instructions: Answer all questions. Choose the best answer for each multiple choice question.

1. What is the primary purpose of encryption in cybersecurity?
A) To speed up data transmission
B) To protect data confidentiality 
C) To compress files
D) To backup data

2. Which of the following is considered a strong password policy?
A) Passwords must be at least 6 characters
B) Passwords can contain only letters
C) Passwords must include uppercase, lowercase, numbers, and symbols
D) Passwords should be shared among team members

3. What does SQL injection attack target?
A) Web browsers
B) Database systems
C) Email servers  
D) Network routers

4. A firewall primarily functions to:
A) Scan for viruses
B) Control network traffic based on rules
C) Encrypt data transmission
D) Backup system files

5. Which authentication method provides the highest security?
A) Single password
B) Two-factor authentication  
C) Username only
D) Biometric identification

6. What is a common characteristic of phishing attacks?
A) They physically damage hardware
B) They attempt to steal credentials through deception
C) They only target corporate networks
D) They require advanced programming skills

7. In cybersecurity, what does VPN stand for?
A) Virtual Private Network
B) Very Protected Network
C) Validated Public Network  
D) Variable Password Network

8. Which of the following is NOT a type of malware?
A) Trojan horse
B) Worm
C) Firewall
D) Ransomware

9. What is the main purpose of access control in information security?
A) To slow down system performance
B) To ensure only authorized users can access resources
C) To backup all system data
D) To monitor internet usage

10. A security audit typically involves:
A) Installing new software
B) Evaluating security policies and procedures
C) Deleting old files
D) Upgrading hardware components
"""

class QuestionDetectionDebugger:
    def __init__(self):
        self.analyzer = LLMQuestionAnalyzer()
        
    async def run_comprehensive_test(self):
        """Run comprehensive test of question detection system"""
        logger.info("="*80)
        logger.info("STARTING COMPREHENSIVE QUESTION DETECTION DEBUG TEST")
        logger.info("="*80)
        
        # Test 1: Analyze sample cybersecurity test
        await self._test_cybersecurity_sample()
        
        # Test 2: Consistency test (run same input multiple times)
        await self._test_consistency()
        
        # Test 3: Edge cases
        await self._test_edge_cases()
        
        logger.info("="*80)
        logger.info("COMPREHENSIVE TEST COMPLETED")
        logger.info("="*80)
    
    async def _test_cybersecurity_sample(self):
        """Test with sample cybersecurity exam"""
        logger.info("\n--- TEST 1: CYBERSECURITY SAMPLE ---")
        
        try:
            result = await self.analyzer.analyze(SAMPLE_CYBERSECURITY_TEST)
            
            questions = result.get('questions', [])
            logger.info(f"RESULT: Found {len(questions)} questions")
            
            # Detailed analysis
            for i, q in enumerate(questions, 1):
                logger.info(f"Question {i}:")
                logger.info(f"  ID: {q.get('question_id')}")
                logger.info(f"  Type: {q.get('question_type')}")
                logger.info(f"  Topic: {q.get('topic')}")
                logger.info(f"  Confidence: {q.get('confidence_score')}")
                logger.info(f"  Detection Method: {q.get('detection_method', 'unknown')}")
                logger.info(f"  Text Preview: {q.get('question_text', '')[:100]}...")
                logger.info("")
            
            # Success metrics
            expected_questions = 10
            detection_rate = len(questions) / expected_questions
            logger.info(f"DETECTION RATE: {detection_rate:.2%} ({len(questions)}/{expected_questions})")
            
            if detection_rate >= 1.0:
                logger.info("✅ SUCCESS: Perfect detection rate achieved!")
            elif detection_rate >= 0.9:
                logger.info("⚠️  GOOD: High detection rate")
            else:
                logger.error("❌ FAILURE: Low detection rate")
                
        except Exception as e:
            logger.error(f"Test failed with error: {e}")
    
    async def _test_consistency(self):
        """Test consistency by running same input multiple times"""
        logger.info("\n--- TEST 2: CONSISTENCY TEST ---")
        
        results = []
        num_runs = 5
        
        for i in range(num_runs):
            logger.info(f"Consistency test run {i+1}/{num_runs}")
            try:
                result = await self.analyzer.analyze(SAMPLE_CYBERSECURITY_TEST)
                question_count = len(result.get('questions', []))
                results.append(question_count)
                logger.info(f"  Run {i+1}: {question_count} questions detected")
            except Exception as e:
                logger.error(f"  Run {i+1}: Failed with error: {e}")
                results.append(0)
        
        # Analyze consistency
        if results:
            avg_questions = sum(results) / len(results)
            min_questions = min(results)
            max_questions = max(results)
            
            logger.info(f"CONSISTENCY ANALYSIS:")
            logger.info(f"  Average: {avg_questions:.1f} questions")
            logger.info(f"  Range: {min_questions} - {max_questions} questions")
            logger.info(f"  Results: {results}")
            
            # Check variance
            variance = max_questions - min_questions
            if variance == 0:
                logger.info("✅ PERFECT CONSISTENCY: No variance between runs")
            elif variance <= 2:
                logger.info("⚠️  ACCEPTABLE CONSISTENCY: Low variance")
            else:
                logger.error("❌ POOR CONSISTENCY: High variance between runs")
    
    async def _test_edge_cases(self):
        """Test edge cases and problematic inputs"""
        logger.info("\n--- TEST 3: EDGE CASES ---")
        
        edge_cases = [
            ("Empty text", ""),
            ("Only instructions", "Instructions: Answer all questions carefully."),
            ("Single question", "1. What is cybersecurity?"),
            ("No numbered questions", "This is just some random text about security."),
            ("Mixed numbering", "1. First question\nA) Some option\n3. Third question")
        ]
        
        for case_name, test_text in edge_cases:
            logger.info(f"Testing: {case_name}")
            try:
                result = await self.analyzer.analyze(test_text)
                question_count = len(result.get('questions', []))
                logger.info(f"  Result: {question_count} questions detected")
            except Exception as e:
                logger.error(f"  Failed: {e}")

async def main():
    """Main debugging function"""
    debugger = QuestionDetectionDebugger()
    await debugger.run_comprehensive_test()

if __name__ == "__main__":
    # Check if OpenAI API key is available
    if not os.getenv('OPENAI_API_KEY'):
        logger.warning("OPENAI_API_KEY not found in environment variables")
        logger.warning("Set your API key: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Run the debugging test
    asyncio.run(main())