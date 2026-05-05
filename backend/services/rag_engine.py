import anthropic
import chromadb 
from chromadb.config import Settings as ChromaSettings
from typing import List

from services.embeddings import EmbeddingService
from models.schemas import DocumentChunk, DocumentMetadata, SourceCitation, QueryResponse
from config import settings

class RAGEngine:
    """
    Manages the vector database.
    Handles storing document chunks and searching them by meaning.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()

        # connect ot ChromaDB (stored locally on disk)
        self.client = chromadb.PersistentClient(
            path=str(settings.chroma_db_dir),
            settings=ChromaSettings(anonymized_telemetry=False)
        )

        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space" : "cosine"}
        )

        self.claude = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        print(f"ChromaDB ready. Total chunks stored: {self.collection.count()}")
    
    # ------------------------------------------------------------------------------------
    # STORE: add a document's chunks to the vector database
    # ------------------------------------------------------------------------------------

    def add_document(self, chunks: List[DocumentChunk], metadata: DocumentMetadata) -> None:
        """
        Embeds all chunks from a document and stores them in ChromaDB.
        """
        if not chunks:
            return
        
        print(f"Embedding {len(chunks)} chunks from '{metadata.filename}'...")

        # embed all chunks in one batch
        texts = [chunk.content for chunk in chunks]
        embeddings = self.embedding_service.embed_batch(texts)

        self.collection.add(
            ids=[chunk.chunk_id for chunk in chunks],
            embeddings=embeddings,
            documents=texts,
            metadatas=[
                {
                    "document_id": chunk.document_id,
                    "filename": chunk.filename,
                    "page_number": chunk.page_number or 0,
                    "chunk_index": chunk.chunk_index,
                    "total_chunks": chunk.total_chunks,
                }
                for chunk in chunks
            ]
        )

        print(f"Stored {len(chunks)} chunks. Total in DB: {self.collection.count()}")
    
    # ------------------------------------------------------------------------------------
    # SEARCH: find the most relevant chunks for a question
    # ------------------------------------------------------------------------------------

    def search(self, question: str, top_k: int = None) -> List[SourceCitation]:
        """
        Embeds the question and finds the closest matching chunks in the DB.
        For small libraries (<=50 chunks), retrieves everything.
        For larger libraries, retrieves top_k most relevant chunks.
        """
        top_k = top_k or settings.top_k_results

        if self.collection.count() == 0:
            return []

        total_chunks = self.collection.count()

        # For small document libraries, retrieve everything so nothing gets missed.
        # For large libraries, use semantic search to find the most relevant chunks.
        n_results = total_chunks if total_chunks <= 50 else min(top_k, total_chunks)

        # Embed the question using the same model as the chunks
        question_embedding = self.embedding_service.embed_text(question)

        # Search ChromaDB for the closest vectors
        results = self.collection.query(
            query_embeddings=[question_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

        # Convert raw results into SourceCitation objects
        citations = []
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for doc, meta, distance in zip(documents, metadatas, distances):
            relevance_score = round(1 - distance, 4)

            citations.append(SourceCitation(
                filename=meta["filename"],
                page_number=meta.get("page_number") or None,
                chunk_index=meta["chunk_index"],
                relevant_excerpt=doc,
                relevance_score=relevance_score,
            ))

        return citations
    
    # ------------------------------------------------------------------------------------
    # MANAGE: list and delete documents
    # ------------------------------------------------------------------------------------

    def list_documents(self) -> List[dict]:
        """ Returns a list of unique documents currently in the DB. """
        if self.collection.count() == 0:
            return []
        
        results = self.collection.get(include=["metadatas"])
        seen = {}
        for meta in results["metadatas"]:
            doc_id = meta["document_id"]
            if doc_id not in seen:
                seen[doc_id] = {
                    "document_id": doc_id,
                    "filename": meta["filename"],
                    "total_chunks": meta["total_chunks"],
                }
        
        return list(seen.values())
    
    def delete_document(self, document_id: str) -> int:
        """ Removes all chunks for a given document from the DB. """
        results = self.collection.get(
            where={"document_id": document_id},
            include=["metadatas"]
        )
        ids_to_delete = results["ids"]
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
        return len(ids_to_delete)
    
    # ------------------------------------------------------------------------------------
    # ANWSER: search + generate a cited answer with Claude
    # ------------------------------------------------------------------------------------

    def answer(self, question: str, top_k: int = None) -> QueryResponse:
        """
        Full RAG pipeline:
        1. search for relevant chunks
        2. build a prompt with those chunks as context
        3. ask Claude to answer using only that context
        4. return the answer + source citations
        """
        
        # step 1: find relevant chunks
        citations = self.search(question, top_k)

        if not citations:
            return QueryResponse(
                question=question,
                answer="I don't have any documents in my knowledge base yet. Please upload some documents first.",
                sources=[]
            )
        
        # step 2: build context block from the retrieved chunks
        context_blocks = []
        for i, citation in enumerate(citations):
            context_blocks.append(
                f"[Source {i+1}: {citation.filename}, page {citation.page_number}]\n"
                f"{citation.relevant_excerpt}"
            )
        context = "\n\n".join(context_blocks)

        # step 3: build the prompt
        prompt = f"""You are a helpful assistant for a business knowledge base.
        Answer the user's question using ONLY the source documents provided below.
        If the answer isn't in the sources, say "I couldn't find that in the uploaded documents."

        SOURCES:
        {context}

        QUESTION:
        {question}

        INSTRUCTIONS:
        - Answer clearly and professionally
        - Reference sources by their number e.g. [Source 1], [Source 2]
        - If multiple sources support the answer, cite all of them
        - Do not make up information not present in the sources
        """

        # step 4: call Claude
        message = self.claude.messages.create(
            model=settings.claude_model,
            max_tokens=settings.max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )

        answer_text = message.content[0].text

        return QueryResponse(
            question=question,
            answer=answer_text,
            sources=citations
        )
