# cramCortex Backend

AI-Powered Test Structure Analyzer Backend

## Quick Start

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the backend server:
```bash
python run.py
```

The server will start on `http://localhost:8000`

## API Endpoints

- `GET /api/v1/health` - Health check
- `POST /api/v1/documents/upload` - Upload PDF documents
- `POST /api/v1/analyze` - Analyze uploaded document and extract questions
- `GET /api/v1/analysis/{document_id}/status` - Get analysis status

## Features Implemented

✅ PDF text extraction with OCR fallback
✅ Question detection and classification
✅ ML-based topic clustering using sentence transformers
✅ Question difficulty estimation
✅ REST API with FastAPI
✅ File upload handling
✅ Error handling and logging

## Architecture

- **PDF Processing**: Uses `unstructured` library with PyMuPDF fallback and pytesseract OCR
- **ML Pipeline**: 
  - Question extraction using regex patterns
  - Sentence embeddings with `sentence-transformers/all-MiniLM-L6-v2`
  - Clustering with HDBSCAN
  - Topic modeling with BERTopic
- **API**: FastAPI with async support and Pydantic schemas

## Directory Structure

```
backend/
├── app/
│   ├── api/          # API route handlers
│   ├── core/         # Configuration
│   ├── schemas/      # Pydantic models
│   └── services/     # Business logic
├── uploads/          # Uploaded files storage
├── requirements.txt  # Python dependencies
└── run.py           # Application entry point
```

## Frontend Integration

The analyze button in the frontend now:
1. Uploads PDF files to the backend
2. Calls the analysis endpoint
3. Displays results with question count, topics, and sample questions
4. Shows real-time progress and error handling