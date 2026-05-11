from fastapi import APIRouter, HTTPException
from models.schemas import QueryRequest, QueryResponse
from services.rag_engine import RAGEngine

router = APIRouter()
rag = RAGEngine()

@router.post("/", response_model=QueryResponse)
def query_knowledge_base(request: QueryRequest):
    """
    Ask a question against the knowledge base.
    Returns an answer with source citations.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        response = rag.answer(request.question, request.top_k, request.document_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/health")
def query_health():
    """ Check how many chunks are avaliable to query. """
    count = rag.collection.count()
    return {
        "status": "ready" if count > 0 else "empty",
        "total_chunks": count
    }