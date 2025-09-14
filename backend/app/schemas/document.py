from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_path: str
    message: str


class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    file_size: int
    content_type: str
    upload_date: datetime
    status: str