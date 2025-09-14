import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

try:
    from unstructured.partition.pdf import partition_pdf
    from unstructured.chunking.title import chunk_by_title
except ImportError:
    partition_pdf = None
    chunk_by_title = None

import pytesseract
from PIL import Image
import fitz  # PyMuPDF

from app.core.config import settings

logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        
    async def extract_text(self, document_id: str) -> Optional[str]:
        """Extract text from PDF document"""
        try:
            # Find document file
            file_path = await self._find_document_file(document_id)
            if not file_path:
                logger.error(f"Document file not found for ID: {document_id}")
                return None
                
            # Extract text using unstructured library
            if partition_pdf:
                text = await self._extract_with_unstructured(file_path)
            else:
                text = await self._extract_with_pymupdf(file_path)
                
            if not text or len(text.strip()) < 50:
                # Fallback to OCR if text extraction failed
                logger.info(f"Low text content, trying OCR for {document_id}")
                text = await self._extract_with_ocr(file_path)
                
            return self._clean_text(text) if text else None
            
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
    
    async def _extract_with_unstructured(self, file_path: Path) -> Optional[str]:
        """Extract text using unstructured library"""
        def _extract():
            try:
                elements = partition_pdf(str(file_path))
                text = "\n".join([str(element) for element in elements])
                return text
            except Exception as e:
                logger.error(f"Unstructured extraction failed: {str(e)}")
                return None
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _extract)
    
    async def _extract_with_pymupdf(self, file_path: Path) -> Optional[str]:
        """Extract text using PyMuPDF"""
        def _extract():
            try:
                doc = fitz.open(str(file_path))
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text
            except Exception as e:
                logger.error(f"PyMuPDF extraction failed: {str(e)}")
                return None
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _extract)
    
    async def _extract_with_ocr(self, file_path: Path) -> Optional[str]:
        """Extract text using OCR with pytesseract"""
        def _extract():
            try:
                doc = fitz.open(str(file_path))
                text = ""
                
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    
                    # Convert to PIL Image
                    from io import BytesIO
                    img = Image.open(BytesIO(img_data))
                    
                    # OCR the image
                    page_text = pytesseract.image_to_string(img, config='--psm 6')
                    text += page_text + "\n"
                
                doc.close()
                return text
            except Exception as e:
                logger.error(f"OCR extraction failed: {str(e)}")
                return None
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _extract)
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess extracted text"""
        if not text:
            return ""
            
        # Remove excessive whitespace
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]  # Remove empty lines
        
        # Join lines back
        cleaned_text = '\n'.join(lines)
        
        # Remove excessive spaces
        import re
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        return cleaned_text.strip()
    
    async def get_document_info(self, document_id: str) -> Dict[str, Any]:
        """Get information about the document"""
        file_path = await self._find_document_file(document_id)
        if not file_path:
            return {}
            
        try:
            doc = fitz.open(str(file_path))
            info = {
                "page_count": doc.page_count,
                "metadata": doc.metadata,
                "file_size": file_path.stat().st_size,
                "file_name": file_path.name
            }
            doc.close()
            return info
        except Exception as e:
            logger.error(f"Error getting document info: {str(e)}")
            return {}