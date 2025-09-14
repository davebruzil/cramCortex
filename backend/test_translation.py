#!/usr/bin/env python3
"""
Test script to validate the Hebrew translation system
"""

import asyncio
import logging
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.hebrew_translator import HebrewTranslator
from app.services.translation_service import TranslationService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_basic_hebrew_translation():
    """Test basic Hebrew to English translation"""
    print("\n🧪 TESTING: Basic Hebrew Translation")
    print("=" * 50)

    translator = HebrewTranslator()

    # Test Hebrew text
    hebrew_text = "שלום עולם! זה מבחן של מערכת התרגום. האם זה עובד?"
    print(f"Input Hebrew: {hebrew_text}")

    result = await translator.translate_hebrew_to_english(hebrew_text)

    print(f"Success: {result['success']}")
    print(f"Hebrew Free Guaranteed: {result.get('hebrew_free_guaranteed', False)}")
    print(f"Translated Text: {result['translated_text']}")

    # Validate no Hebrew characters
    if translator._contains_hebrew_characters(result['translated_text']):
        print("❌ FAILED: Translation still contains Hebrew characters!")
        hebrew_chars = translator._extract_hebrew_characters(result['translated_text'])
        print(f"Hebrew characters found: {hebrew_chars}")
        return False
    else:
        print("✅ PASSED: No Hebrew characters detected in output")
        return True


async def test_exam_question_translation():
    """Test Hebrew exam question translation"""
    print("\n🧪 TESTING: Hebrew Exam Question Translation")
    print("=" * 50)

    service = TranslationService()

    # Hebrew exam question
    hebrew_exam = """
1. מה זה אבטחת מידע?
א) הגנה על מחשבים בלבד
ב) הגנה על נתונים ומידע
ג) תוכנת אנטי וירוס
ד) כל התשובות נכונות

2. איזה מהבאים הוא דוגמה להתקפת פישינג?
א) התקפת DDoS
ב) אימייל מזויף שמבקש סיסמאות
ג) וירוס במחשב
ד) פריצה פיזית למשרד
"""

    print(f"Input Hebrew Exam:")
    print(hebrew_exam)
    print("\n" + "─" * 30)

    result = await service.translate_exam_document(hebrew_exam)

    print(f"Success: {result['success']}")
    print(f"Hebrew Free: {result.get('hebrew_free_guaranteed', 'Unknown')}")
    print(f"Translated Exam:")
    print(result['translated_text'])

    # Validate no Hebrew characters
    translator = HebrewTranslator()
    if translator._contains_hebrew_characters(result['translated_text']):
        print("❌ FAILED: Translation still contains Hebrew characters!")
        hebrew_chars = translator._extract_hebrew_characters(result['translated_text'])
        print(f"Hebrew characters found: {hebrew_chars}")
        return False
    else:
        print("✅ PASSED: No Hebrew characters detected in output")
        return True


async def test_mixed_content():
    """Test mixed Hebrew/English content"""
    print("\n🧪 TESTING: Mixed Hebrew/English Content")
    print("=" * 50)

    translator = HebrewTranslator()

    mixed_text = """
Instructions: This is an English instruction.
שאלה 1: מה המשמעות של TCP/IP?
Question 2: What does HTTP stand for?
תשובה: זה פרוטוקול תקשורת.
Answer: It's a communication protocol.
"""

    print(f"Input Mixed Content:")
    print(mixed_text)
    print("\n" + "─" * 30)

    result = await translator.translate_hebrew_to_english(mixed_text)

    print(f"Success: {result['success']}")
    print(f"Translated Text:")
    print(result['translated_text'])

    # Validate no Hebrew characters
    if translator._contains_hebrew_characters(result['translated_text']):
        print("❌ FAILED: Translation still contains Hebrew characters!")
        hebrew_chars = translator._extract_hebrew_characters(result['translated_text'])
        print(f"Hebrew characters found: {hebrew_chars}")
        return False
    else:
        print("✅ PASSED: No Hebrew characters detected in output")
        return True


async def test_large_document():
    """Test large Hebrew document with chunking"""
    print("\n🧪 TESTING: Large Document with Chunking")
    print("=" * 50)

    translator = HebrewTranslator()

    # Create a large Hebrew document
    large_hebrew = """
מבחן באבטחת מידע ומחשבים

1. מה זה firewall?
א) תוכנה להגנה מפני וירוסים
ב) מערכת להגנה על רשת מפני גישה לא מורשית
ג) כלי לגיבוי נתונים
ד) תוכנה לעריכת טקסט

2. איזה מהבאים הוא סוג של malware?
א) HTTP
ב) TCP/IP
ג) Trojan Horse
ד) DNS

3. מה המשמעות של SSL?
א) Simple System Language
ב) Secure Socket Layer
ג) System Security Lock
ד) Standard Software License

4. איזו מהשיטות הבאות היא הטובה ביותר לאבטחת סיסמאות?
א) להשתמש באותה סיסמה לכל האתרים
ב) לכתוב את הסיסמה על פתק
ג) להשתמש בסיסמאות חזקות וייחודיות
ד) לשתף את הסיסמה עם חברים

5. מה זה phishing?
א) טכניקת דיג
ב) התקפה שמטרתה לגנוב מידע אישי
ג) תוכנת אנטי וירוס
ד) פרוטוקול רשת

6. איזה מהבאים הוא דוגמה לאימות דו-שלבי?
א) רק סיסמה
ב) סיסמה וקוד SMS
ג) רק טביעת אצבע
ד) רק כרטיס מגנטי

7. מה זה DDoS?
א) Data Distribution over Systems
ב) Distributed Denial of Service
ג) Digital Data on Servers
ד) Dynamic Domain Service

8. איזו מהשיטות הבאות היא הטובה ביותר לגיבוי נתונים?
א) לשמור עותק אחד במחשב
ב) לשמור עותקים במספר מקומות שונים
ג) לא לעשות גיבוי כלל
ד) לשמור רק בדיסק חיצוני

9. מה המשמעות של VPN?
א) Very Private Network
ב) Virtual Personal Network
ג) Virtual Private Network
ד) Verified Protection Network

10. איזה מהבאים הוא סימן להדבקה בווירוס?
א) המחשב עובד מהר יותר
ב) המחשב נבלם או עובד לאט
ג) הזיכרון פנוי יותר
ד) כל התוכנות עובדות בצורה מושלמת
""" * 2  # Duplicate to make it larger

    print(f"Large document length: {len(large_hebrew)} characters")

    result = await translator.translate_hebrew_to_english(large_hebrew)

    print(f"Success: {result['success']}")
    print(f"Original chunks: {result.get('original_chunks', 0)}")
    print(f"Hebrew Free Guaranteed: {result.get('hebrew_free_guaranteed', False)}")
    print(f"Translation preview (first 500 chars):")
    print(result['translated_text'][:500] + "...")

    # Validate no Hebrew characters
    if translator._contains_hebrew_characters(result['translated_text']):
        print("❌ FAILED: Translation still contains Hebrew characters!")
        hebrew_chars = translator._extract_hebrew_characters(result['translated_text'])
        print(f"Hebrew characters found: {hebrew_chars}")
        return False
    else:
        print("✅ PASSED: No Hebrew characters detected in output")
        return True


async def run_all_tests():
    """Run all translation tests"""
    print("🚀 STARTING COMPREHENSIVE TRANSLATION TESTS")
    print("=" * 60)

    tests = [
        ("Basic Hebrew Translation", test_basic_hebrew_translation),
        ("Exam Question Translation", test_exam_question_translation),
        ("Mixed Content", test_mixed_content),
        ("Large Document", test_large_document)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {str(e)}")
            results.append((test_name, False))

    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Translation system is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

    return passed == total


if __name__ == "__main__":
    asyncio.run(run_all_tests())