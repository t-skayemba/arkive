import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from services.document_processor import DocumentProcessor
from services.rag_engine import RAGEngine
from config import settings

router = APIRouter()
processor = DocumentProcessor()
rag = RAGEngine()

ALLOWED_TYPES = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """ Upload a document to the knowledge base. """
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{suffix}' not supported. Use PDF, DOCX, or TXT."
        )
    
    if not file.filename or len(file.filename) > 255:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    
    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(status_code = 400, detail="The uploaded file is empty.")
    
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        size_mb = round(len(file_bytes) / 1024 / 1024, 1)
        raise HTTPException(
            status_code=400,
            detail=f"File size is {size_mb}MB - maximum allowed is {MAX_FILE_SIZE_MB}MB."
        )
    
    if suffix == ".pdf":
        _check_pdf_not_encrypted(file_bytes)

    save_path = settings.upload_dir / file.filename
    try:
        with open(save_path, "wb") as f:
            f.write(file_bytes)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    try:
        metadata, chunks = processor.process_file(save_path, file.filename)
    except ValueError as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Could not extract text from '{file.filename}'. The file may be corrupted, scanned, or contain only images. Details: {str(e)}")

    if not chunks:
        save_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=422,
            detail=f"No text could be extracted from '{file.filename}'. The file may be blank, image-only, or use an unsupported encoding."
        )
    
    try:
        rag.add_document(chunks, metadata)
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Failed to index document: {str(e)}")
    
    return {
        "message": f"Successfully uploaded and indexed '{file.filename}'",
        "document_id": metadata.document_id,
        "filename": metadata.filename,
        "total_chunks": metadata.total_chunks,
        "file_size_kb": metadata.file_size_kb,
    }

def _check_pdf_not_encrypted(file_bytes: bytes) -> None:
    """Raises HTTPException is the PDF is password-protected."""
    try:
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(file_bytes))
        if reader.is_encrypted:
            raise HTTPException(
                status_code=400,
                detail="This PDF is password-protected. Please remove the password and re-upload."
            )
    except HTTPException:
        raise
    except Exception:
        pass

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