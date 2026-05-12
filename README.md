# Arkive

**Stop searching your documents. Start asking them questions.**

Arkive is an enterprise-ready RAG (Retrieval-Augmented Generation) knowledge base that lets you upload documents and ask natural language questions — getting accurate, cited answers grounded in your actual files.

---

## Try It Live

🚀 **[arkive.tianakayemba.dev](https://arkive.tianakayemba.dev)** — no setup required!

---

## What It Does

Upload your documents and Arkive will:

- **Answer questions in natural language** — ask anything, get cited answers backed by your documents
- **Extract text from PDFs, DOCX, and TXT files** — including tables, grade breakdowns, schedules, and structured data
- **Cite every answer** — each response shows exactly which source and page the information came from
- **Filter by document** — scope your question to a specific file when you have multiple documents loaded
- **Rate confidence** — High/Medium/Low confidence badge per answer based on source relevance
- **Preview documents** — click any file in the library to view its full content with relevant passages highlighted
- **Track your session** — live stats for documents indexed, chunks stored, queries run, and average relevance
- **Copy answers** — one-click copy on any AI response for pasting into emails or reports
- **Validate uploads** — catches password-protected PDFs, empty files, oversized files, and corrupted documents with clear error messages
- **Log every query** — full observability via Langfuse: latency, token usage, retrieved sources, and answers logged per query

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, FastAPI, Uvicorn |
| **Vector Database** | ChromaDB (local, persistent) |
| **Embeddings** | sentence-transformers (`all-MiniLM-L6-v2`) |
| **AI** | Anthropic Claude API (`claude-sonnet-4-6`) |
| **Document Parsing** | pypdf, python-docx, chardet |
| **Observability** | Langfuse (query logging, latency, token tracking) |
| **Frontend** | React, Vite, Tailwind CSS v4 |
| **HTTP Client** | Axios |
| **Deployment** | Railway, custom domain |

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/t-skayemba/arkive.git
cd arkive
```

### 2. Set up the backend

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **Note:** Python 3.12 is required. Python 3.13+ is not yet supported by all dependencies.

### 3. Set your API keys

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```
ANTHROPIC_API_KEY=your_anthropic_key_here
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

Get an Anthropic key at [console.anthropic.com](https://console.anthropic.com)
Get a free Langfuse account at [cloud.langfuse.com](https://cloud.langfuse.com)

### 4. Start the backend

```bash
uvicorn main:app --reload --port 8000
```

### 5. Set up and start the frontend

```bash
cd ../frontend
npm install
npm run dev
```

Visit `http://localhost:5173`

---

## How to Use

1. **Upload a document** — drag and drop or click the upload zone. Supports PDF, DOCX, TXT up to 20MB
2. **Ask a question** — type any natural language question and press Enter
3. **Filter by document** — use the dropdown above the input bar to search within a specific file
4. **Review the answer** — cited answer with source cards showing which passages were used
5. **Preview the document** — click any file in the Library to view full text with cited passages highlighted
6. **Delete a document** — hover over a file in the Library and click the trash icon

---

## Configuration

All settings are in `backend/config.py`:

| Setting | Default | Description |
|---|---|---|
| `chunk_size` | 600 | Characters per text chunk |
| `chunk_overlap` | 150 | Overlap between chunks for context continuity |
| `top_k_results` | 25 | Max chunks retrieved per query |
| `embedding_model` | `all-MiniLM-L6-v2` | Local embedding model |
| `claude_model` | `claude-sonnet-4-6` | Claude model used for generation |

---

## Input Validation

Arkive validates every upload before indexing:

| Check | Limit | Error shown |
|---|---|---|
| File type | PDF, DOCX, TXT only | Unsupported file type |
| File size | Max 20MB | File too large |
| Empty file | Must have content | File is empty |
| Password-protected PDF | Not supported | Password-protected PDF |
| Corrupted/image-only PDF | Must have extractable text | Could not read PDF |
| Corrupted DOCX | Must be valid Word document | Not a valid Word document |

---

## Observability

Every query is logged to Langfuse with:
- The question asked and any document filter applied
- Number of chunks retrieved and top relevance score
- The full prompt sent to Claude
- Claude's response
- Input and output token counts
- End-to-end latency in milliseconds

---

## Data & Privacy

| What | Where |
|---|---|
| Uploaded files | Stored locally in `backend/data/uploads/` |
| Vector embeddings | Stored locally in `backend/data/chroma_db/` |
| Query processing | Sent to Anthropic's API to generate answers |
| Query logs | Sent to Langfuse for observability |

Files and vectors never leave your machine. Query text and relevant document excerpts are sent to Anthropic's API for answer generation. See [Anthropic's Privacy Policy](https://www.anthropic.com/privacy) for details.

---

## Project Structure

```
arkive/
├── backend/
│   ├── main.py                      # FastAPI app entry point
│   ├── config.py                    # All settings in one place
│   ├── requirements.txt             # Python dependencies
│   ├── .env                         # API keys (not committed)
│   ├── .env.example                 # Template for required keys
│   ├── routers/
│   │   ├── documents.py             # Upload, list, delete, preview endpoints
│   │   └── query.py                 # Question answering endpoint
│   ├── services/
│   │   ├── document_processor.py    # PDF/DOCX/TXT extraction and chunking
│   │   ├── embeddings.py            # sentence-transformers embedding service
│   │   └── rag_engine.py            # Vector search + Claude + Langfuse logging
│   ├── models/
│   │   └── schemas.py               # Pydantic data models
│   └── data/
│       ├── uploads/                 # Uploaded document files
│       └── chroma_db/               # ChromaDB vector store
└── frontend/
    └── src/
        ├── App.jsx                  # Root layout and state
        ├── utils/
        │   └── api.js               # Axios API client
        └── components/
            ├── DocumentUpload.jsx   # Drag and drop upload with validation
            ├── DocumentLibrary.jsx  # File list with delete and preview
            ├── DocumentPreview.jsx  # Full text modal with highlights
            ├── QueryInterface.jsx   # Chat UI with document filter dropdown
            └── SourceCard.jsx       # Citation card component
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/documents/upload` | Upload and index a document |
| `GET` | `/documents/list` | List all indexed documents |
| `DELETE` | `/documents/{id}` | Remove a document |
| `GET` | `/documents/{id}/content` | Get full document text for preview |
| `POST` | `/query/` | Ask a question, optionally filter by document_id |
| `GET` | `/query/health` | Check how many chunks are available |

Interactive docs available at `http://localhost:8000/docs` when the backend is running.

---

## Future Enhancements

- Multi-document filtering (search across a selected subset of documents)
- Folder/collection grouping for large document libraries
- Re-index all documents button
- OCR support for scanned PDFs
- Fully local LLM option via Ollama for air-gapped deployments

---

Built by [Tiana Kayemba](https://github.com/t-skayemba)

## License
MIT