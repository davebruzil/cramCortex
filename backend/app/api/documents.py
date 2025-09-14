from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
import uuid
from pathlib import Path

from app.core.config import settings
from app.schemas.document import DocumentResponse, DocumentUploadResponse

router = APIRouter()


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for analysis"""
    
    # Use safe encoding for filenames with Unicode characters
    safe_filename = file.filename.encode('ascii', errors='replace').decode('ascii') if file.filename else 'unknown'
    print(f"Upload request received for file: {safe_filename}")
    print(f"Content type: {file.content_type}")
    
    # Validate file type
    if not file.content_type.startswith(('application/pdf', 'image/')):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF and image files are supported"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_extension = Path(file.filename).suffix
    filename = f"{file_id}{file_extension}"
    file_path = upload_dir / filename
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    return DocumentUploadResponse(
        document_id=file_id,
        filename=file.filename,
        file_path=str(file_path),
        message="Document uploaded successfully"
    )


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents():
    """List all uploaded documents"""
    # TODO: Implement document listing from database
    return []


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    # TODO: Implement document deletion
    return {"message": f"Document {document_id} deleted successfully"}