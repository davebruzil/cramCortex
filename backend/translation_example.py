#!/usr/bin/env python3
"""
Example usage of the Hebrew Translation System
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.translation_service import TranslationService


async def translate_hebrew_exam():
    """
    Example: Translate a Hebrew cybersecurity exam to English
    """
    print("🔄 Translating Hebrew Cybersecurity Exam...")

    # Sample Hebrew exam content
    hebrew_exam = """
מבחן באבטחת מחשבים ומידע

1. מה זו חומת אש (Firewall)?
א) תוכנה המגנה מפני וירוסים
ב) מכשיר החוסם גישה לא מורשית לרשת
ג) תוכנה לגיבוי קבצים
ד) מערכת הפעלה מאובטחת

2. איזה מהבאים הוא סוג של תוכנה זדונית?
א) וירוס
ב) תולעת (Worm)
ג) סוס טרויאני (Trojan)
ד) כל התשובות נכונות

3. מה המשמעות של HTTPS?
א) HyperText Transfer Protocol Secure
ב) High Text Transfer Protocol System
ג) Hyper Transfer Text Protocol Safe
ד) HyperText Transmission Protocol Security

4. איזו מהשיטות הבאות היא הטובה ביותר לאבטחת סיסמאות?
א) להשתמש בסיסמה אחת לכל האתרים
ב) לשמור סיסמאות בקובץ טקסט
ג) להשתמש בסיסמאות חזקות וייחודיות לכל אתר
ד) לשתף סיסמאות עם עמיתים לעבודה

5. מה זה דיוג (Phishing)?
א) שיטת דיג במחשב
ב) התקפה שמטרתה לגנוב מידע אישי
ג) תוכנה להגנה על המחשב
ד) פרוטוקול להעברת קבצים
"""

    # Initialize translation service
    translator = TranslationService()

    try:
        # Translate the exam
        result = await translator.translate_exam_document(hebrew_exam)

        # Display results
        print(f"✅ Translation Status: {'Success' if result['success'] else 'Failed'}")
        print(f"📊 Hebrew-Free Guaranteed: {result.get('hebrew_free_guaranteed', 'No')}")

        if result.get('original_chunks'):
            print(f"📝 Processed {result['original_chunks']} chunks")

        print("\n" + "="*60)
        print("📄 TRANSLATED EXAM (English)")
        print("="*60)
        print(result['translated_text'])
        print("="*60)

        return result

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


async def translate_simple_text():
    """
    Example: Translate simple Hebrew text
    """
    print("\n🔄 Translating Simple Hebrew Text...")

    hebrew_text = "שלום! זה טקסט לדוגמה באבטחת מחשבים. האם התרגום עובד כמו שצריך?"

    translator = TranslationService()

    try:
        result = await translator.translate_document(
            content=hebrew_text,
            source_language="hebrew",
            target_language="english"
        )

        print(f"Original Hebrew: {hebrew_text}")
        print(f"English Translation: {result['translated_text']}")
        print(f"Success: {result['success']}")

        return result

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


async def batch_translate_example():
    """
    Example: Batch translate multiple Hebrew text chunks
    """
    print("\n🔄 Batch Translation Example...")

    hebrew_chunks = [
        "מה זה אבטחת מידע?",
        "איך עובדת הצפנה?",
        "מדוע חשובה הגנה על סיסמאות?",
        "איזה סוגי התקפות קיימים ברשת?"
    ]

    translator = TranslationService()

    try:
        result = await translator.batch_translate_chunks(hebrew_chunks)

        print(f"Batch Translation Results:")
        print(f"- Total chunks: {result['total_chunks']}")
        print(f"- Successful: {result['successful_chunks']}")
        print(f"- Success rate: {result['success_rate']*100:.1f}%")

        print("\nTranslated chunks:")
        for i, chunk_data in enumerate(result['chunk_details']):
            print(f"{i+1}. {chunk_data['translated']}")

        return result

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


async def main():
    """
    Main example function demonstrating all translation capabilities
    """
    print("🚀 Hebrew Translation System - Usage Examples")
    print("="*60)

    # Example 1: Translate a Hebrew exam
    await translate_hebrew_exam()

    # Example 2: Simple text translation
    await translate_simple_text()

    # Example 3: Batch translation
    await batch_translate_example()

    # Show service capabilities
    translator = TranslationService()
    capabilities = translator.get_service_info()

    print("\n📋 Translation Service Capabilities:")
    print(f"- Service: {capabilities['service_name']} v{capabilities['version']}")
    print(f"- Supported languages: {capabilities['supported_languages']['source_languages']} → {capabilities['supported_languages']['target_languages']}")
    print(f"- Max chunk size: {capabilities['performance']['max_chunk_size']} characters")
    print(f"- Concurrent processing: {capabilities['performance']['concurrent_chunks']} chunks")

    print("\n✨ Done! All examples completed.")


if __name__ == "__main__":
    asyncio.run(main())