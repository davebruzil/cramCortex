import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import PyPDF2

from app.core.config import settings

logger = logging.getLogger(__name__)


class SimplePDFParser:
    def __init__(self):
        pass
        
    async def extract_text(self, document_id: str) -> Optional[str]:
        """Extract text from PDF using PyPDF2"""
        try:
            file_path = await self._find_document_file(document_id)
            if not file_path:
                logger.error(f"Document file not found for ID: {document_id}")
                return None
            
            logger.info(f"Extracting text from: {file_path}")
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                logger.info(f"PDF has {len(pdf_reader.pages)} pages")
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        text += f"\n--- Page {page_num + 1} ---\n"
                        text += page_text
                        logger.info(f"Extracted {len(page_text)} characters from page {page_num + 1}")
                    except Exception as e:
                        logger.error(f"Error extracting page {page_num + 1}: {str(e)}")
                        continue
                
                cleaned_text = self._clean_text(text)
                logger.info(f"Total extracted text length: {len(cleaned_text)} characters")
                return cleaned_text
                
        except Exception as e:
            logger.error(f"Error extracting text from {document_id}: {str(e)}")
            return None
    
    async def _find_document_file(self, document_id: str) -> Optional[Path]:
        """Find the document file by ID"""
        upload_dir = Path(settings.UPLOAD_DIR)
        
        if not upload_dir.exists():
            logger.error(f"Upload directory does not exist: {upload_dir}")
            return None
        
        # Look for files with the document_id
        for file_path in upload_dir.glob(f"{document_id}.*"):
            if file_path.is_file():
                logger.info(f"Found document file: {file_path}")
                return file_path
        
        logger.error(f"No file found for document_id: {document_id}")        
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace while preserving structure
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Keep non-empty lines
                cleaned_lines.append(line)
        
        # Join lines back with single newlines
        cleaned_text = '\n'.join(cleaned_lines)
        
        return cleaned_text
    
    async def get_document_info(self, document_id: str) -> Dict[str, Any]:
        """Get basic information about the PDF document"""
        file_path = await self._find_document_file(document_id)
        if not file_path:
            return {}
            
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                info = {
                    "page_count": len(pdf_reader.pages),
                    "file_size": file_path.stat().st_size,
                    "file_name": file_path.name,
                    "metadata": {}
                }
                
                # Try to get PDF metadata
                if pdf_reader.metadata:
                    info["metadata"] = {
                        "title": pdf_reader.metadata.get('/Title', ''),
                        "author": pdf_reader.metadata.get('/Author', ''),
                        "subject": pdf_reader.metadata.get('/Subject', ''),
                        "creator": pdf_reader.metadata.get('/Creator', '')
                    }
                
                return info
                
        except Exception as e:
            logger.error(f"Error getting document info: {str(e)}")
            return {}