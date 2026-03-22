"""
Sahay AI - Embedder Service
===========================

Multilingual embedding generation using sentence-transformers.
Uses multilingual-e5-large for strong cross-lingual recall.

Author: Jagadeep Mamidi
"""

import logging
from typing import List, Optional

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EmbedderService:
    """
    Service for generating multilingual embeddings.

    Uses multilingual-e5-large which supports 100+ languages
    including Telugu, Hindi, Tamil, Kannada, etc.

    E5 models require a prefix:
    - 'passage: ' for documents
    - 'query: ' for user queries
    """

    def __init__(self, model_name: str = None):
        settings = get_settings()
        self.model_name = model_name or settings.embedding_model

        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        logger.info(
            f"Model loaded. Dimension: {self.model.get_sentence_embedding_dimension()}"
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed documents/passages for storage.

        Args:
            texts: List of text documents to embed

        Returns:
            List of embedding vectors (1024 dimensions for multilingual-e5-large)
        """
        prefixed = [f"passage: {text}" for text in texts]
        embeddings = self.model.encode(
            prefixed, normalize_embeddings=True, show_progress_bar=True
        )
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Embed a user query for similarity search.

        Args:
            query: User query text (can be in any supported language)

        Returns:
            Query embedding vector (1024 dimensions)
        """
        prefixed = f"query: {query}"
        embedding = self.model.encode(
            prefixed, normalize_embeddings=True, show_progress_bar=False
        )
        return embedding.tolist()

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Embed texts in batches without any e5 prefix (raw encoding).

        .. warning::
            This method does NOT add the required ``'passage: '`` or ``'query: '``
            prefixes expected by multilingual-e5-large.  Use it only when you
            intentionally want unprefixed embeddings (e.g. custom downstream
            processing).

            - For **document ingestion** use :meth:`embed_documents` (adds ``'passage: '``).
            - For **query embedding** use :meth:`embed_query` (adds ``'query: '``).

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch

        Returns:
            List of raw embedding vectors
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        return embeddings.tolist()

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self.model.get_sentence_embedding_dimension()

    @property
    def max_seq_length(self) -> int:
        """Get maximum sequence length."""
        return self.model.max_seq_length


_embedder_service: Optional[EmbedderService] = None


def get_embedder() -> EmbedderService:
    """Get or create singleton embedder service."""
    global _embedder_service
    if _embedder_service is None:
        _embedder_service = EmbedderService()
    return _embedder_service
