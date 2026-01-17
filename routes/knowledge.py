"""
Al-Mudeer - Knowledge Base API
Endpoints for adding and querying the RAG system.
"""

from fastapi import APIRouter, HTTPException, Depends, Header, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from services.knowledge_base import get_knowledge_base
import io

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])

class AddDocumentRequest(BaseModel):
    text: str = Field(..., min_length=10, description="The content to add")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata (title, source, etc.)")

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3)
    k: int = Field(3, ge=1, le=10)

@router.post("/add")
async def add_document(request: AddDocumentRequest):
    """Add a document to the Knowledge Base"""
    kb = get_knowledge_base()
    success = await kb.add_document(request.text, request.metadata)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add document")
        
    return {"success": True, "message": "Document added successfully"}

@router.post("/search")
async def search_knowledge(request: SearchRequest):
    """Test search endpoint"""
    kb = get_knowledge_base()
    results = await kb.search(request.query, request.k)
    
    return {"results": results}

@router.get("/list")
@router.get("/documents")
async def list_documents(limit: int = 100):
    """List documents in the Knowledge Base"""
    kb = get_knowledge_base()
    docs = await kb.list_documents(limit)
    return {"documents": docs}

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a file (PDF/Text) to Knowledge Base"""
    kb = get_knowledge_base()
    content = ""
    
    try:
        if file.filename.endswith(".pdf"):
            try:
                import pypdf
            except ImportError:
                 raise HTTPException(status_code=500, detail="pypdf not installed")
            
            reader = pypdf.PdfReader(file.file)
            for page in reader.pages:
                content += page.extract_text() + "\n"
        else:
            # Assume text
            content_bytes = await file.read()
            content = content_bytes.decode("utf-8", errors="ignore")
            
        if len(content) < 10:
            raise HTTPException(status_code=400, detail="File content too short or empty")
            
        success = await kb.add_document(content, {"source": file.filename, "type": "pdf" if file.filename.endswith(".pdf") else "text"})
        if not success:
             raise HTTPException(status_code=500, detail="Failed to index document")
             
        return {"success": True, "message": f"Processed {file.filename}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
