from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).parent

class Settings(BaseSettings):
    # API Keys
    anthropic_api_key: str = ""

    # Paths
    upload_dir: Path = BASE_DIR / "data" / "uploads"
    chroma_db_dir: Path = BASE_DIR / "data" / "chroma_db"

    # RAG Settings
    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k_results: int = 7
    embedding_model: str = "all-MiniLM-L6-v2"

    # Claude Settings
    claude_model: str = "claude-sonnet-4-6"
    max_tokens: int = 1500

    # App Settings
    app_name: str = "RAG Knowledge Base"
    version: str = "1.0.0"
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173", "https://arkive.tianakayemba.dev", "https://victorious-kindness-production.up.railway.app"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# ensure directories exist on startup
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.chroma_db_dir.mkdir(parents=True, exist_ok=True)