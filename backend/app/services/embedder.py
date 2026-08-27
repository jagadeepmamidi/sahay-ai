"""
Sahay AI - Embedder Service
===========================

Optional document embedder for admin PDF ingestion only.
The chat query path does not load this model.
"""

import logging
from typing import List, Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EmbedderService:
    def __init__(self, model_name: str = None):
        settings = get_settings()
        self.model_name = model_name or settings.embedding_model
        self.model = None
        logger.info("Embedder is lazy. Model %s will load only if ingest is used.", self.model_name)

    def _ensure_model(self):
        if self.model is not None:
            return
        from sentence_transformers import SentenceTransformer

        logger.info("Loading optional embedding model: %s", self.model_name)
        self.model = SentenceTransformer(self.model_name)

    def embed_documents(self, texts: List[str], batch_size: int = 96) -> List[List[float]]:
        self._ensure_model()
        prefixed = [f"passage: {text}" for text in texts]
        embeddings = self.model.encode(
            prefixed,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        self._ensure_model()
        embedding = self.model.encode(
            f"query: {query}", normalize_embeddings=True, show_progress_bar=False
        )
        return embedding.tolist()

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        self._ensure_model()
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        self._ensure_model()
        return self.model.get_sentence_embedding_dimension()

    @property
    def max_seq_length(self) -> int:
        self._ensure_model()
        return self.model.max_seq_length


_embedder_service: Optional[EmbedderService] = None


def get_embedder() -> EmbedderService:
    global _embedder_service
    if _embedder_service is None:
        _embedder_service = EmbedderService()
    return _embedder_service
