from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from routers import documents, query
from config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Enterprise RAG Knowledge Base API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/documents", tags=["Documents"])
app.include_router(query.router, prefix="/query", tags=["Query"])

@app.get("/")
def health_check():
    return {"status": "ok", "app": settings.app_name, "version": settings.version}