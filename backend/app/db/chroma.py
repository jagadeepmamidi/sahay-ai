"""
Sahay AI - ChromaDB Client
==========================

Local vector database for RAG pipeline.
ChromaDB is persistent, free, and runs locally.

Author: Jagadeep Mamidi
"""

import os
import sqlite3
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings

from app.core.config import get_settings


class ChromaDBClient:
    """ChromaDB client for storing and retrieving scheme embeddings."""

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: str = "sahay_schemes",
    ):
        settings = get_settings()
        self.persist_dir = persist_directory or settings.chroma_persist_path
        self.collection_name = collection_name

        os.makedirs(self.persist_dir, exist_ok=True)

        try:
            self.client = chromadb.PersistentClient(
                path=self.persist_dir,
                settings=Settings(
                    allow_reset=True,
                    anonymized_telemetry=False,
                ),
            )

            self.collection = self.client.get_or_create_collection(
                name=self.collection_name, metadata={"hnsw:space": "cosine"}
            )
        except (sqlite3.OperationalError, KeyError) as exc:
            raise RuntimeError(
                "ChromaDB schema is incompatible with the installed chromadb package. "
                "Upgrade the environment to the version pinned in backend/requirements.txt, "
                "then rebuild or reindex the persisted collection "
                f"at {self.persist_dir}."
            ) from exc

    def upsert(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        """Insert or update vectors in the collection."""
        self.collection.upsert(
            ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
        )

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 10,
        where: Optional[Dict] = None,
        where_document: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Query the collection for similar vectors."""
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=["documents", "metadatas", "distances"],
        )

    def get(
        self,
        ids: Optional[List[str]] = None,
        where: Optional[Dict] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get vectors by ID or filter."""
        return self.collection.get(
            ids=ids, where=where, limit=limit, include=["documents", "metadatas"]
        )

    def count(self) -> int:
        """Get total number of vectors in collection."""
        return self.collection.count()

    def delete(self, ids: List[str]) -> None:
        """Delete vectors by ID."""
        self.collection.delete(ids=ids)

    def reset(self) -> None:
        """Reset the collection (deletes all data)."""
        self.client.reset()

    def peek(self, limit: int = 10) -> Dict[str, Any]:
        """Peek at first N items in collection."""
        return self.collection.peek(limit=limit)


_chroma_client: Optional[ChromaDBClient] = None


def get_chroma_client() -> ChromaDBClient:
    """Get or create singleton ChromaDB client."""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = ChromaDBClient()
    return _chroma_client
