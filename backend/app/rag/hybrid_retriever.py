"""
Hybrid Retriever (BM25 + ChromaDB Vector Search)
=================================================

True hybrid retrieval combining BM25 keyword search with ChromaDB
semantic vector search using multilingual-e5-large embeddings (1024d).

Author: Jagadeep Mamidi
"""

import logging
import re
from typing import Any, Dict, List, Optional

import numpy as np
from rank_bm25 import BM25Okapi

from app.core.config import get_settings
from app.db.chroma import get_chroma_client

logger = logging.getLogger(__name__)

settings = get_settings()


class HybridRetriever:
    """
    Hybrid retriever that combines:
    - BM25 keyword matching (good for exact scheme names, terms)
    - ChromaDB vector similarity (good for semantic/conceptual matches)

    Results are merged and re-ranked using weighted combination.
    """

    def __init__(self):
        self.bm25 = None
        self.documents: List[Dict] = []
        self.tokenized_corpus: List[List[str]] = []
        self.chroma_collection = None
        self._chroma_client = None

        # Initialize ChromaDB
        self._init_chromadb()

        # Load documents from ChromaDB if available
        self._load_from_chromadb()

    def _init_chromadb(self):
        """Initialize ChromaDB with persistent storage."""
        try:
            chroma = get_chroma_client()
            self._chroma_client = chroma.client
            self.chroma_collection = chroma.collection

            count = self.chroma_collection.count()
            logger.info(
                f"ChromaDB initialized at {chroma.persist_dir} with {count} documents"
            )
        except Exception as e:
            logger.error(
                f"ChromaDB initialization failed: {e}. Running BM25-only mode."
            )

    def _sync_chroma_collection(self):
        """Refresh the retriever's collection handle from the singleton client."""
        try:
            chroma = get_chroma_client()
            self._chroma_client = chroma.client
            self.chroma_collection = chroma.collection
        except Exception as e:
            logger.error(f"Failed to sync ChromaDB collection: {e}")
            self.chroma_collection = None

    def _load_from_chromadb(self):
        """Load existing documents from ChromaDB to build BM25 index."""
        self._sync_chroma_collection()
        if not self.chroma_collection:
            logger.info("No ChromaDB collection. Loading sample documents for BM25.")
            self._load_sample_documents()
            return

        count = self.chroma_collection.count()
        if count == 0:
            logger.info("ChromaDB is empty. Loading sample documents for BM25.")
            self._load_sample_documents()
            return

        # Load all documents from ChromaDB for BM25 index
        try:
            results = self.chroma_collection.get(include=["documents", "metadatas"])

            for i, doc_id in enumerate(results["ids"]):
                self.documents.append(
                    {
                        "id": doc_id,
                        "content": results["documents"][i],
                        "metadata": results["metadatas"][i] or {},
                    }
                )

            self._append_sample_documents_if_missing()
            self._build_bm25_index()
            logger.info(
                f"Loaded {len(self.documents)} documents from ChromaDB for BM25"
            )

        except Exception as e:
            logger.error(f"Failed to load from ChromaDB: {e}")
            self._load_sample_documents()

    def _append_sample_documents_if_missing(self):
        """
        Ensure critical flagship schemes remain searchable in BM25 even when
        Chroma contains a narrower domain dataset (e.g., scholarships only).
        """
        existing_ids = {doc["id"] for doc in self.documents}
        for sample in self._get_sample_documents():
            if sample["id"] not in existing_ids:
                self.documents.append(sample)

    def _load_sample_documents(self):
        """Load sample scheme documents as fallback."""
        self.documents = self._get_sample_documents()
        self._build_bm25_index()
        logger.info(f"Loaded {len(self.documents)} sample documents (fallback mode)")

    def _get_sample_documents(self) -> List[Dict]:
        """Return built-in sample scheme documents."""
        return [
            {
                "id": "pm-kisan-1",
                "content": """PM-KISAN (Pradhan Mantri Kisan Samman Nidhi) is a Central Sector scheme with 100%
                funding from Government of India. Under the scheme, income support of Rs. 6000 per year
                is provided to all farmer families across the country in three equal installments of
                Rs. 2000 each every four months. The fund is directly transferred to the bank accounts
                of the beneficiaries.""",
                "metadata": {
                    "scheme_id": "pm-kisan",
                    "scheme_name": "PM-KISAN",
                    "category": "Agriculture",
                    "benefit_summary": "₹6,000 per year",
                    "eligibility_summary": "All landholding farmer families",
                },
            },
            {
                "id": "pmjay-1",
                "content": """Ayushman Bharat PM-JAY (Pradhan Mantri Jan Arogya Yojana) is the world's largest
                health insurance scheme providing free health coverage of up to Rs. 5 lakh per family
                per year for secondary and tertiary care hospitalization. Over 10.74 crore poor and
                vulnerable families (approximately 50 crore beneficiaries) are entitled.""",
                "metadata": {
                    "scheme_id": "pm-ayushman",
                    "scheme_name": "Ayushman Bharat PM-JAY",
                    "category": "Health",
                    "benefit_summary": "Up to ₹5 lakh health coverage",
                    "eligibility_summary": "BPL families as per SECC 2011",
                },
            },
            {
                "id": "pmay-1",
                "content": """Pradhan Mantri Awaas Yojana Gramin (PMAY-G) provides financial assistance of
                Rs. 1.20 lakh in plain areas and Rs. 1.30 lakh in hilly/difficult areas for construction
                of pucca house. Beneficiaries are identified from SECC-2011 database.""",
                "metadata": {
                    "scheme_id": "pm-awas-gramin",
                    "scheme_name": "PMAY-G",
                    "category": "Housing",
                    "benefit_summary": "₹1.20-1.30 lakh for house construction",
                    "eligibility_summary": "Houseless rural BPL families",
                },
            },
        ]

    def _build_bm25_index(self):
        """Build BM25 index from current documents."""
        if not self.documents:
            return

        self.tokenized_corpus = [
            self._tokenize_for_search(doc) for doc in self.documents
        ]

        self.bm25 = BM25Okapi(self.tokenized_corpus)
        logger.info(f"BM25 index built with {len(self.tokenized_corpus)} documents")

    def _normalize_search_text(self, text: str) -> str:
        """Normalize text so hyphenated scheme names match natural user queries."""
        cleaned = (text or "").lower()
        cleaned = re.sub(r"[-_/]", " ", cleaned)
        cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)
        return cleaned.strip()

    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text for BM25 using normalized alphanumeric terms."""
        normalized = self._normalize_search_text(text)
        return [token for token in normalized.split() if token]

    def _tokenize_for_search(self, doc: Dict) -> List[str]:
        """Include scheme metadata in BM25 so exact scheme-name searches rank correctly."""
        metadata = doc.get("metadata") or {}
        searchable_parts = [
            doc.get("content", ""),
            metadata.get("scheme_name", ""),
            metadata.get("scheme_id", ""),
            metadata.get("category", ""),
            metadata.get("benefit_summary", ""),
            metadata.get("eligibility_summary", ""),
        ]
        return self._tokenize_text(
            " ".join(str(part) for part in searchable_parts if part)
        )

    def _scheme_match_boost(self, query: str, doc: Dict) -> float:
        """Boost results that explicitly mention the queried scheme name."""
        normalized_query = self._normalize_search_text(query)
        if not normalized_query:
            return 0.0

        query_tokens = set(normalized_query.split())
        metadata = doc.get("metadata") or {}
        searchable = " ".join(
            [
                self._normalize_search_text(doc.get("content", "")),
                self._normalize_search_text(str(metadata.get("scheme_name", ""))),
                self._normalize_search_text(str(metadata.get("scheme_id", ""))),
            ]
        )
        searchable_tokens = set(searchable.split())

        if normalized_query in searchable:
            return 0.35
        if query_tokens and query_tokens.issubset(searchable_tokens):
            return 0.2
        return 0.0

    def _embed_text(self, query: str) -> Optional[List[float]]:
        """
        Generate QUERY embedding using multilingual-e5-large (1024d).
        Uses the required 'query: ' prefix for the e5 model family.
        Falls back to None if embedding fails.
        """
        try:
            from app.services.embedder import get_embedder

            embedder = get_embedder()
            return embedder.embed_query(query)
        except Exception as e:
            logger.error(f"Query embedding generation failed: {e}")
            return None

    def _embed_document(self, content: str) -> Optional[List[float]]:
        """
        Generate PASSAGE embedding using multilingual-e5-large (1024d).
        Uses the required 'passage: ' prefix for the e5 model family.
        Falls back to None if embedding fails.
        """
        try:
            from app.services.embedder import get_embedder

            embedder = get_embedder()
            return embedder.embed_documents([content])[0]
        except Exception as e:
            logger.error(f"Document embedding generation failed: {e}")
            return None

    def _embed_texts_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate PASSAGE embeddings for a batch of texts using multilingual-e5-large (1024d).
        Uses the required 'passage: ' prefix for the e5 model family.
        """
        try:
            from app.services.embedder import get_embedder

            embedder = get_embedder()
            return embedder.embed_documents(texts)
        except Exception as e:
            logger.error(f"Batch document embedding failed: {e}")
            return []

    def add_document(self, doc_id: str, content: str, metadata: Dict = None):
        """Add a single document to both BM25 and ChromaDB."""
        doc = {"id": doc_id, "content": content, "metadata": metadata or {}}

        # Add to BM25
        self.documents.append(doc)
        self.tokenized_corpus.append(self._tokenize_for_search(doc))
        self.bm25 = BM25Okapi(self.tokenized_corpus)

        # Add to ChromaDB with passage embedding (multilingual-e5-large, 'passage: ' prefix)
        self._sync_chroma_collection()
        if self.chroma_collection:
            try:
                embedding = self._embed_document(content)
                if embedding:
                    # ChromaDB requires string metadata values
                    clean_metadata = {k: str(v) for k, v in (metadata or {}).items()}
                    self.chroma_collection.add(
                        ids=[doc_id],
                        documents=[content],
                        embeddings=[embedding],
                        metadatas=[clean_metadata],
                    )
                    logger.debug(f"Added document {doc_id} to ChromaDB")
                else:
                    # Add without embedding, ChromaDB will use default
                    clean_metadata = {k: str(v) for k, v in (metadata or {}).items()}
                    self.chroma_collection.add(
                        ids=[doc_id], documents=[content], metadatas=[clean_metadata]
                    )
            except Exception as e:
                logger.error(f"Failed to add to ChromaDB: {e}")

    def add_documents_batch(self, documents: List[Dict]):
        """
        Add multiple documents at once (more efficient for bulk ingestion).
        Each dict should have: id, content, metadata
        """
        if not documents:
            return

        ids = [d["id"] for d in documents]
        contents = [d["content"] for d in documents]
        metadatas = [
            {k: str(v) for k, v in (d.get("metadata") or {}).items()} for d in documents
        ]

        # Add to BM25
        for doc in documents:
            self.documents.append(doc)
            self.tokenized_corpus.append(self._tokenize_for_search(doc))
        self.bm25 = BM25Okapi(self.tokenized_corpus)

        # Add to ChromaDB in batch
        self._sync_chroma_collection()
        if self.chroma_collection:
            try:
                embeddings = self._embed_texts_batch(contents)
                if embeddings and len(embeddings) == len(ids):
                    self.chroma_collection.add(
                        ids=ids,
                        documents=contents,
                        embeddings=embeddings,
                        metadatas=metadatas,
                    )
                else:
                    # Fallback: add without embeddings
                    self.chroma_collection.add(
                        ids=ids, documents=contents, metadatas=metadatas
                    )
                logger.info(f"Added {len(ids)} documents to ChromaDB")
            except Exception as e:
                logger.error(f"Batch add to ChromaDB failed: {e}")

    def search(self, query: str, top_k: int = 5, alpha: float = 0.5) -> List[Dict]:
        """
        Hybrid search combining BM25 and vector search.

        Args:
            query: Search query
            top_k: Number of results to return
            alpha: Weight for vector search (0=BM25 only, 1=vector only, 0.5=balanced)

        Returns:
            List of matching documents, scored and ranked
        """
        bm25_results = self._bm25_search(query, top_k=top_k * 2)
        vector_results = self._vector_search(query, top_k=top_k * 2)

        # If only one method returned results, use that
        if not vector_results:
            return bm25_results[:top_k]
        if not bm25_results:
            return vector_results[:top_k]

        # Merge and re-rank
        return self._merge_results(bm25_results, vector_results, query, alpha, top_k)

    def _bm25_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """BM25 keyword search."""
        if not self.bm25 or not self.documents:
            return []

        tokenized_query = self._tokenize_text(query)
        if not tokenized_query:
            return []
        scores = self.bm25.get_scores(tokenized_query)

        # Normalize scores
        max_score = max(scores) if max(scores) > 0 else 1
        normalized = scores / max_score

        top_indices = sorted(
            range(len(normalized)), key=lambda i: normalized[i], reverse=True
        )[:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append(
                    {
                        **self.documents[idx],
                        "score": float(normalized[idx])
                        + self._scheme_match_boost(query, self.documents[idx]),
                        "search_type": "bm25",
                    }
                )

        results.sort(key=lambda doc: doc["score"], reverse=True)
        return results

    def _vector_search(self, query: str, top_k: int = 10) -> List[Dict]:
        """ChromaDB vector similarity search."""
        self._sync_chroma_collection()
        if not self.chroma_collection or self.chroma_collection.count() == 0:
            return []

        try:
            # Generate query embedding
            query_embedding = self._embed_text(query)

            if query_embedding:
                results = self.chroma_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(top_k, self.chroma_collection.count()),
                    include=["documents", "metadatas", "distances"],
                )
            else:
                # Fallback: use ChromaDB's built-in text search
                results = self.chroma_collection.query(
                    query_texts=[query],
                    n_results=min(top_k, self.chroma_collection.count()),
                    include=["documents", "metadatas", "distances"],
                )

            output = []
            if results and results["ids"] and results["ids"][0]:
                for i, doc_id in enumerate(results["ids"][0]):
                    # ChromaDB returns distances; convert to similarity
                    distance = results["distances"][0][i] if results["distances"] else 0
                    similarity = max(0, 1 - distance)

                    output.append(
                        {
                            "id": doc_id,
                            "content": results["documents"][0][i],
                            "metadata": results["metadatas"][0][i] or {},
                            "score": similarity,
                            "search_type": "vector",
                        }
                    )

            return output

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

    def _merge_results(
        self,
        bm25_results: List[Dict],
        vector_results: List[Dict],
        query: str,
        alpha: float,
        top_k: int,
    ) -> List[Dict]:
        """
        Merge BM25 and vector results using weighted combination.
        alpha controls the balance: 0 = BM25 only, 1 = vector only.
        """
        combined = {}

        # Add BM25 results
        for doc in bm25_results:
            doc_id = doc["id"]
            combined[doc_id] = {
                **doc,
                "bm25_score": doc["score"],
                "vector_score": 0.0,
                "search_type": "bm25",
            }

        # Merge vector results
        for doc in vector_results:
            doc_id = doc["id"]
            if doc_id in combined:
                combined[doc_id]["vector_score"] = doc["score"]
                combined[doc_id]["search_type"] = "hybrid"
            else:
                combined[doc_id] = {
                    **doc,
                    "bm25_score": 0.0,
                    "vector_score": doc["score"],
                    "search_type": "vector",
                }

        # Calculate combined scores
        for doc_id, doc in combined.items():
            doc["score"] = (
                (1 - alpha) * doc["bm25_score"] + alpha * doc["vector_score"]
            ) + self._scheme_match_boost(query, doc)

        # Sort by combined score
        ranked = sorted(combined.values(), key=lambda x: x["score"], reverse=True)

        return ranked[:top_k]

    def clear_all(self):
        """Clear all documents from both indexes."""
        self.documents = []
        self.tokenized_corpus = []
        self.bm25 = None

        if self.chroma_collection:
            try:
                # Delete and recreate collection
                self._chroma_client.delete_collection("sahay_schemes")
                self.chroma_collection = self._chroma_client.get_or_create_collection(
                    name="sahay_schemes", metadata={"hnsw:space": "cosine"}
                )
                logger.info("Cleared all documents from ChromaDB")
            except Exception as e:
                logger.error(f"Failed to clear ChromaDB: {e}")

    def get_stats(self) -> Dict:
        """Get retriever statistics."""
        self._sync_chroma_collection()
        chroma_count = 0
        if self.chroma_collection:
            try:
                chroma_count = self.chroma_collection.count()
            except Exception:
                pass

        return {
            "bm25_documents": len(self.documents),
            "chromadb_documents": chroma_count,
            "has_vector_search": self.chroma_collection is not None,
            "mode": "hybrid"
            if self.chroma_collection and chroma_count > 0
            else "bm25_only",
        }


# Singleton instance
_retriever: Optional[HybridRetriever] = None


def get_retriever() -> HybridRetriever:
    """Get singleton retriever instance."""
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever


def reset_retriever():
    """Reset retriever (useful after reindexing)."""
    global _retriever
    _retriever = None
