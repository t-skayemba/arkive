import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

from services.document_processor import DocumentProcessor
from services.rag_engine import RAGEngine
from config import settings

router = APIRouter()
processor = DocumentProcessor()
rag = RAGEngine()

ALLOWED_TYPES = {".pdf", ".docx", ".txt"}


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{suffix}' not supported. Use PDF, DOCX, or TXT."
        )

    save_path = settings.upload_dir / file.filename
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        metadata, chunks = processor.process_file(save_path, file.filename)
        rag.add_document(chunks, metadata)
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

    return {
        "message": f"Successfully uploaded and indexed '{file.filename}'",
        "document_id": metadata.document_id,
        "filename": metadata.filename,
        "total_chunks": metadata.total_chunks,
        "file_size_kb": metadata.file_size_kb,
    }


@router.get("/list")
def list_documents():
    documents = rag.list_documents()
    return {"documents": documents, "total": len(documents)}


@router.delete("/{document_id}")
def delete_document(document_id: str):
    deleted_count = rag.delete_document(document_id)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": f"Deleted document and {deleted_count} chunks"}


@router.get("/{document_id}/content")
def get_document_content(document_id: str):
    """
    Returns clean full text of a document for preview.
    Re-reads original file instead of joining chunks (avoids duplicates from overlap).
    """
    # Look up filename from stored chunks
    results = rag.collection.get(
        where={"document_id": document_id},
        include=["metadatas"]
    )
    if not results["ids"]:
        raise HTTPException(status_code=404, detail="Document not found")

    filename = results["metadatas"][0]["filename"]
    file_path = settings.upload_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Original file not found on disk")

    # Re-extract full clean text (no chunking, no overlap)
    full_text = processor.extract_full_text(file_path)

    return {
        "document_id": document_id,
        "filename": filename,
        "content": full_text
    }