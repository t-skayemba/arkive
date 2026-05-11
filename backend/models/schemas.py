from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentChunk(BaseModel):
    """ A single chunk of text from a document, with source metadata. """
    chunk_id: str
    document_id: str
    filename: str
    content: str
    page_number: Optional[int] = None
    chunk_index: int
    total_chunks: int

class DocumentMetadata(BaseModel):
    """ Info about an uploaded document. """
    document_id: str
    filename: str
    file_type: str
    total_chunks: int
    upload_time: datetime
    file_size_kb: float

class QueryRequest(BaseModel):
    """ A user question sent to the RAG engine. """
    question: str
    top_k: Optional[int] = 5
    document_id: Optional[str] = None

class SourceCitation(BaseModel):
    """ A source that was used to answer a question. """
    filename: str
    page_number: Optional[int]
    chunk_index: int
    relevant_excerpt: str
    relevance_score: float

class QueryResponse(BaseModel):
    """ The full answer returned to the user. """
    answer: str
    sources: list[SourceCitation]
    question: str
