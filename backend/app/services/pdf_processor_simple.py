import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import asyncio

from app.core.config import settings

logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self):
        pass
        
    async def extract_text(self, document_id: str) -> Optional[str]:
        """Mock PDF text extraction for testing"""
        try:
            file_path = await self._find_document_file(document_id)
            if not file_path:
                return None
                
            # For now, return mock text that looks like exam questions
            mock_text = """
            1. What is the capital of France?
            A) London
            B) Berlin  
            C) Paris
            D) Madrid
            
            2. Which of the following is a programming language?
            A) HTML
            B) CSS
            C) Python
            D) SQL
            
            3. What does CPU stand for?
            A) Computer Processing Unit
            B) Central Processing Unit
            C) Central Program Unit
            D) Computer Program Unit
            
            4. Explain the difference between supervised and unsupervised learning.
            
            5. True or False: JavaScript is the same as Java.
            """
            
            return mock_text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from {document_id}: {str(e)}")
            return None
    
    async def _find_document_file(self, document_id: str) -> Optional[Path]:
        """Find the document file by ID"""
        upload_dir = Path(settings.UPLOAD_DIR)
        
        # Look for files with the document_id
        for file_path in upload_dir.glob(f"{document_id}.*"):
            if file_path.is_file():
                return file_path
                
        return None
    
    async def get_document_info(self, document_id: str) -> Dict[str, Any]:
        """Get information about the document"""
        file_path = await self._find_document_file(document_id)
        if not file_path:
            return {}
            
        try:
            info = {
                "page_count": 1,
                "metadata": {"title": "Mock PDF"},
                "file_size": file_path.stat().st_size if file_path.exists() else 0,
                "file_name": file_path.name if file_path else "mock.pdf"
            }
            return info
        except Exception as e:
            logger.error(f"Error getting document info: {str(e)}")
            return {}