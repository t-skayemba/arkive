import uuid
import re
from pathlib import Path
from typing import List 
from datetime import datetime

from models.schemas import DocumentChunk, DocumentMetadata
from config import settings

class DocumentProcessor:
    """
    Handles reading, cleaning, and chunking uploaded documents.
    Supports PDF, DOCX, and TXT file types.
    """

    def __init__(self):
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap

    def process_file(self, file_path: Path, filename: str) -> tuple[DocumentMetadata, List[DocumentChunk]]:
        """
        Takes a file, extracts text, chunks it, and returns metadata + chunks.
        This is the only method you need to call from outside this class.
        """

        document_id = str(uuid.uuid4())
        file_type = file_path.suffix.lower()
        file_size_kb = round(file_path.stat().st_size / 1024, 2)

        # extract raw text (with page numbers where possible)
        pages = self._extract_text(file_path, file_type)

        # chunk all the pages into small pieces
        chunks = self._create_chunks(pages, document_id, filename)

        # build the metadata summary
        metadata = DocumentMetadata(
            document_id=document_id,
            filename=filename,
            file_type=file_type,
            total_chunks=len(chunks),
            upload_time=datetime.now(),
            file_size_kb=file_size_kb,
        )

        return metadata, chunks

        # ---------------------------------------------------------------------------------------------------------
        # Extract text from each file type
        # ---------------------------------------------------------------------------------------------------------

    def _extract_text(self, file_path: Path, file_type: str) -> List[dict]:
        """
        Returns a list of {page_number, text} dicts.
        PDFs use real page numbers. DOXC and TXT use page 1.
        """
        if file_type == ".pdf":
            return self._extract_pdf(file_path)
        elif file_type == ".docx":
            return self._extract_docx(file_path)
        elif file_type == ".txt":
            return self._extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported file tupe: {file_type}")
        
    def _extract_pdf(self, file_path: Path) -> List[dict]:
        from pypdf import PdfReader
        reader = PdfReader(str(file_path))
        pages = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                pages.append({"page_number": i + 1, "text": self._clean_text(text)})
        return pages
        
    def _extract_docx(self, file_path: Path) -> List[dict]:
        from docx import Document
        doc = Document(str(file_path))
        parts = []

        for p in doc.paragraphs:
            if p.text.strip():
                parts.append(p.text.strip())

        for table in doc.tables:
            for row in table.rows:
                seen = []
                for cell in row.cells:
                    text = cell.text.strip()
                    if text and text not in seen:
                        seen.append(text)
                if seen:
                    parts.append(' | '.join(seen))

        return [{"page_number": 1, "text": self._clean_text("\n".join(parts))}]
        
    def _extract_txt(self, file_path: Path) -> List[dict]:
        import chardet
        raw = file_path.read_bytes()
        encoding = chardet.detect(raw)["encoding"] or "utf-8"
        text = raw.decode(encoding)
        return [{"page_number": 1, "text": self._clean_text(text)}]
        
    # ---------------------------------------------------------------------------------------------------------
    # Clean the text
    # ---------------------------------------------------------------------------------------------------------

    def _clean_text(self, text: str) -> str:
        """ Remove junk characters, extra whitespace, and blank lines. """
        text = re.sub(r'\s+', ' ', text)                # collapse multiple spaces/newlines
        text = re.sub(r'[^\x20-\x7E\n]', ' ', text)     # remove non-printable characters
        text = re.sub(r'\n{3,}', '\n\n', text)          # max 2 consecutive newlines
        return text.strip()
        
    # ---------------------------------------------------------------------------------------------------------
    # Split into overlapping chunks
    # ---------------------------------------------------------------------------------------------------------

    def _create_chunks(self, pages: List[dict], document_id: str, filename: str) -> List[DocumentChunk]:
        """
        Splits each page's text into overlapping chunks.
        Overlap ensures that sentences split across chunk boundaries are still findable.
        """
        all_chunks = []
        chunk_index = 0

        for page in pages:
            text = page["text"]
            page_number = page["page_number"]

            start = 0
            while start < len(text):
                end = start + self.chunk_size
                chunk_text = text[start:end]

                if len(chunk_text.strip()) < 50:
                    break
                    
                all_chunks.append(DocumentChunk(
                    chunk_id=str(uuid.uuid4()),
                    document_id=document_id,
                    filename=filename,
                    content=chunk_text.strip(),
                    page_number=page_number,
                    chunk_index=chunk_index,
                    total_chunks=0, # filled in after loop
                ))

                chunk_index += 1
                start += self.chunk_size - self.chunk_overlap
                
            total = len(all_chunks)
            for chunk in all_chunks:
                chunk.total_chunks = total
                
            return all_chunks

    def extract_full_text(self, file_path: Path) -> str:
        """Returns complete document text without chunking — used for preview."""
        file_type = file_path.suffix.lower()
        pages = self._extract_text(file_path, file_type)
        return "\n\n".join(page["text"] for page in pages)