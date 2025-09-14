from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any

from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.simple_pdf_parser import SimplePDFParser
from app.services.llm_question_analyzer import LLMQuestionAnalyzer

router = APIRouter()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Analyze a document and extract questions"""
    
    try:
        print(f"Starting analysis for document: {request.document_id}")
        
        # Initialize processors
        pdf_processor = SimplePDFParser()
        question_analyzer = LLMQuestionAnalyzer()
        
        print("Processors initialized")
        
        # Extract text from document
        extracted_text = await pdf_processor.extract_text(request.document_id)
        print(f"Extracted text length: {len(extracted_text) if extracted_text else 0}")
        
        if not extracted_text:
            print("No text extracted from document")
            raise HTTPException(status_code=400, detail="No text could be extracted from document")
        
        # Analyze questions
        print("Starting question analysis...")
        analysis_result = await question_analyzer.analyze(extracted_text)
        print(f"Analysis complete. Found {len(analysis_result.get('questions', []))} questions")
        
        return AnalysisResponse(
            document_id=request.document_id,
            status="completed",
            questions_found=len(analysis_result.get("questions", [])),
            topics_identified=len(analysis_result.get("topics", [])),
            analysis_data=analysis_result
        )
        
    except Exception as e:
        print(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/analysis/{document_id}/status")
async def get_analysis_status(document_id: str) -> Dict[str, Any]:
    """Get the status of document analysis"""
    # TODO: Implement status tracking
    return {
        "document_id": document_id,
        "status": "pending",
        "progress": 0
    }