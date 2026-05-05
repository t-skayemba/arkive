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
- **Rate confidence** — Medium/High/Low confidence badge per answer based on source relevance
- **Preview documents** — click any file in the library to view its full content with relevant passages highlighted
- **Track your session** — live stats for documents indexed, chunks stored, queries run, and average relevance
- **Copy answers** — one-click copy on any AI response for pasting into emails or reports

---

## Try It Live

🚀 **[arkive.tianakayemba.dev](https://arkive.tianakayemba.dev)** — no setup required!

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, FastAPI, Uvicorn |
| **Vector Database** | ChromaDB (local, persistent) |
| **Embeddings** | sentence-transformers (`all-MiniLM-L6-v2`) |
| **AI** | Anthropic Claude API (`claude-sonnet-4-6`) |
| **Document Parsing** | pypdf, python-docx, chardet |
| **Frontend** | React, Vite, Tailwind CSS v4 |
| **HTTP Client** | Axios |

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

### 3. Set your API key

```bash
cp .env.example .env
```

Open `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

Get a key at [console.anthropic.com](https://console.anthropic.com)

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

1. **Upload a document** — drag and drop or click the upload zone in the sidebar. Supports PDF, DOCX, and TXT
2. **Ask a question** — type any natural language question in the chat input and press Enter
3. **Review the answer** — Arkive returns a cited answer with source cards showing which passages were used
4. **Preview the document** — click any file in the Library to view its full text with cited passages highlighted in purple
5. **Delete a document** — hover over a file in the Library and click the trash icon to remove it from the knowledge base

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

## Data & Privacy

| What | Where |
|---|---|
| Uploaded files | Stored locally in `backend/data/uploads/` |
| Vector embeddings | Stored locally in `backend/data/chroma_db/` |
| Query processing | Sent to Anthropic's API to generate answers |

Files and vectors never leave your machine. Query text and relevant document excerpts are sent to Anthropic's API for answer generation. See [Anthropic's Privacy Policy](https://www.anthropic.com/privacy) for details.

---

## Project Structure

```
arkive/
├── backend/
│   ├── main.py                      # FastAPI app entry point
│   ├── config.py                    # All settings in one place
│   ├── requirements.txt             # Python dependencies
│   ├── .env                         # API key (not committed)
│   ├── routers/
│   │   ├── documents.py             # Upload, list, delete, preview endpoints
│   │   └── query.py                 # Question answering endpoint
│   ├── services/
│   │   ├── document_processor.py    # PDF/DOCX/TXT extraction and chunking
│   │   ├── embeddings.py            # sentence-transformers embedding service
│   │   └── rag_engine.py            # Vector search + Claude answer generation
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
            ├── DocumentUpload.jsx   # Drag and drop upload zone
            ├── DocumentLibrary.jsx  # File list with delete and preview
            ├── DocumentPreview.jsx  # Full text modal with highlights
            ├── QueryInterface.jsx   # Chat UI with skeleton loader
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
| `POST` | `/query/` | Ask a question, get a cited answer |
| `GET` | `/query/health` | Check how many chunks are available |

Interactive docs available at `http://localhost:8000/docs` when the backend is running.

---

Built by [Tiana Kayemba](https://github.com/t-skayemba)

## License
MIT