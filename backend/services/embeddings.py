from sentence_transformers import SentenceTransformer
from config import settings
from utils.logger import get_logger

logger=get_logger(__name__)

class EmbeddingService:
    """
    Converts text into vectors using local sentence-transformers model.
    No API calls needed - runs entirely on your machine.
    """

    def __init__(self):
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        self.model = SentenceTransformer(settings.embedding_model)
        logger.info("Embedding model ready")
    
    def embed_text(self, text: str) -> list[float]:
        """ Convert a single string into a vector. """
        return self.model.encode(text, convert_to_numpy=True).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """ Convert a list of strings into vectors - faster than one at a time. """
        return self.model.encode(texts, convert_to_numpy=True).tolist()