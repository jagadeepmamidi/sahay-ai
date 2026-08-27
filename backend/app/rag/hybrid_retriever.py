"""
Scheme-level hybrid retriever
=============================

Query path is lexical only: BM25 + alias/field matching + eligibility boost.
No neural embedding model is loaded at request time.

ChromaDB remains an optional supplement for uploaded PDFs. Those documents
are pulled as text and merged into the same BM25 index.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from rank_bm25 import BM25Okapi

from app.knowledge.catalog import load_catalog
from app.rag.query_parser import parse_query

logger = logging.getLogger(__name__)


def _normalize(text: str) -> str:
    cleaned = (text or "").lower()
    cleaned = re.sub(r"[-_/]", " ", cleaned)
    cleaned = re.sub(r"[^a-z0-9\u0900-\u097f\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _tokenize(text: str) -> List[str]:
    return [token for token in _normalize(text).split() if token]


class HybridRetriever:
    """Scheme-first retriever with optional Chroma text supplements."""

    def __init__(self):
        self.documents: List[Dict[str, Any]] = []
        self.tokenized_corpus: List[List[str]] = []
        self.bm25: Optional[BM25Okapi] = None
        self.chroma_collection = None
        self._chroma_client = None
        self._load_catalog_documents()
        self._load_chroma_supplements()
        self._build_bm25_index()

    def _load_catalog_documents(self) -> None:
        for scheme in load_catalog():
            self.documents.append(self._scheme_to_document(scheme))

    def _scheme_to_document(self, scheme: Dict[str, Any]) -> Dict[str, Any]:
        content = (
            f"{scheme.get('full_name') or scheme['name']}. "
            f"{scheme.get('description', '')} "
            f"Benefits: {scheme.get('benefits', '')} "
            f"Eligibility: {scheme.get('eligibility_summary', '')} "
            f"How to apply: {scheme.get('application_process', '')}"
        )
        return {
            "id": scheme["id"],
            "content": content,
            "source": "catalog",
            "scheme": scheme,
            "metadata": {
                "scheme_id": scheme["id"],
                "scheme_name": scheme["name"],
                "full_name": scheme.get("full_name", scheme["name"]),
                "category": scheme.get("category", ""),
                "benefit_summary": scheme.get("benefit_amount") or scheme.get("benefits", ""),
                "eligibility_summary": scheme.get("eligibility_summary", ""),
                "apply_url": scheme.get("apply_url"),
                "ministry": scheme.get("ministry", ""),
            },
        }

    def _load_chroma_supplements(self) -> None:
        """Load extra PDF chunks as text only. Never embed at query time."""
        try:
            from app.db.chroma import get_chroma_client

            chroma = get_chroma_client()
            self._chroma_client = chroma.client
            self.chroma_collection = chroma.collection
            count = chroma.count()
            if count == 0:
                return
            rows = chroma.get(limit=min(count, 2000))
            ids = rows.get("ids") or []
            docs = rows.get("documents") or []
            metas = rows.get("metadatas") or []
            existing = {doc["id"] for doc in self.documents}
            added = 0
            for idx, chunk_id in enumerate(ids):
                metadata = metas[idx] or {}
                scheme_id = str(metadata.get("scheme_id") or chunk_id)
                if scheme_id in existing:
                    continue
                content = (docs[idx] or "").strip()
                if not content:
                    continue
                self.documents.append(
                    {
                        "id": str(chunk_id),
                        "content": content,
                        "source": "chroma",
                        "scheme": None,
                        "metadata": {
                            "scheme_id": scheme_id,
                            "scheme_name": metadata.get("scheme_name")
                            or metadata.get("name")
                            or scheme_id,
                            "category": metadata.get("category", "General"),
                            "benefit_summary": metadata.get("benefit_summary", ""),
                            "eligibility_summary": metadata.get("eligibility_summary", ""),
                            "apply_url": metadata.get("apply_url")
                            or metadata.get("source_url"),
                        },
                    }
                )
                existing.add(scheme_id)
                added += 1
            if added:
                logger.info("Loaded %s Chroma text supplements into BM25", added)
        except Exception as exc:
            logger.info("Chroma supplements skipped: %s", exc)
            self.chroma_collection = None

    def _build_bm25_index(self) -> None:
        self.tokenized_corpus = [
            _tokenize(self._searchable_text(doc)) for doc in self.documents
        ]
        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)
        logger.info("Retriever ready with %s documents", len(self.documents))

    def _searchable_text(self, doc: Dict[str, Any]) -> str:
        metadata = doc.get("metadata") or {}
        scheme = doc.get("scheme") or {}
        parts = [
            doc.get("content", ""),
            metadata.get("scheme_name", ""),
            metadata.get("scheme_id", ""),
            metadata.get("category", ""),
            metadata.get("benefit_summary", ""),
            metadata.get("eligibility_summary", ""),
            " ".join(scheme.get("aliases") or []),
            " ".join(scheme.get("tags") or []),
        ]
        return " ".join(str(part) for part in parts if part)

    def _alias_boost(self, query: str, doc: Dict[str, Any]) -> float:
        normalized_query = _normalize(query)
        if not normalized_query:
            return 0.0
        scheme = doc.get("scheme") or {}
        metadata = doc.get("metadata") or {}
        names = [
            metadata.get("scheme_id", ""),
            metadata.get("scheme_name", ""),
            metadata.get("full_name", ""),
            *(scheme.get("aliases") or []),
        ]
        best = 0.0
        for name in names:
            alias = _normalize(str(name))
            if not alias:
                continue
            if alias == normalized_query or alias in normalized_query:
                best = max(best, 0.55 if len(alias) >= 5 else 0.35)
            elif normalized_query in alias:
                best = max(best, 0.3)
        return best

    def _profile_boost(self, doc: Dict[str, Any], profile: Optional[Dict[str, Any]]) -> float:
        if not profile:
            return 0.0
        scheme = doc.get("scheme") or {}
        rules = scheme.get("eligibility") or {}
        score = 0.0
        occupation = (profile.get("occupation") or "").lower()
        occupations = [o.lower() for o in rules.get("occupations") or []]
        if occupation and occupations and occupation in occupations:
            score += 0.22
        if profile.get("is_bpl") and rules.get("is_bpl"):
            score += 0.12
        if profile.get("has_land") and rules.get("has_land"):
            score += 0.12
        gender = (profile.get("gender") or "").lower()
        if gender and rules.get("gender") == gender:
            score += 0.08
        return score

    def search(
        self,
        query: str,
        top_k: int = 5,
        alpha: float = 0.35,
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Rank schemes for a user query.

        alpha is retained for API compatibility. The current ranker is lexical
        (BM25 + alias/field match + eligibility boost). Neural vector search
        is intentionally skipped on the query path.
        """
        parsed = parse_query(query, user_profile)
        if not self.bm25 or not self.documents:
            return []

        tokenized_query = _tokenize(parsed["normalized_query"] or query)
        if not tokenized_query:
            tokenized_query = _tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        max_score = max(scores) if len(scores) and max(scores) > 0 else 1.0

        ranked: List[Dict[str, Any]] = []
        for idx, doc in enumerate(self.documents):
            bm25_score = float(scores[idx] / max_score) if max_score else 0.0
            alias = self._alias_boost(query, doc)
            if parsed["scheme_ids"] and doc.get("id") in parsed["scheme_ids"]:
                alias = max(alias, 0.6)
            if parsed.get("category"):
                if (doc.get("metadata") or {}).get("category") == parsed["category"]:
                    alias += 0.12
            if parsed.get("occupation"):
                tags = " ".join((doc.get("scheme") or {}).get("tags") or [])
                if parsed["occupation"] in _normalize(tags + " " + doc.get("content", "")):
                    alias += 0.08
            combined = ((1 - alpha) * bm25_score) + (alpha * alias) + alias
            combined += self._profile_boost(doc, user_profile)
            if combined <= 0:
                continue
            ranked.append(
                {
                    **doc,
                    "score": round(float(combined), 4),
                    "bm25_score": round(bm25_score, 4),
                    "vector_score": 0.0,
                    "search_type": "hybrid" if alias else "bm25",
                }
            )

        ranked.sort(key=lambda item: item["score"], reverse=True)

        # Deduplicate by scheme_id, keeping the strongest hit.
        seen = set()
        unique: List[Dict[str, Any]] = []
        for doc in ranked:
            scheme_id = (doc.get("metadata") or {}).get("scheme_id") or doc["id"]
            if scheme_id in seen:
                continue
            seen.add(scheme_id)
            unique.append(doc)
            if len(unique) >= top_k:
                break
        return unique

    def add_document(self, doc_id: str, content: str, metadata: Dict = None):
        """Add a supplemental document to the BM25 index. Embeddings are optional."""
        metadata = metadata or {}
        doc = {
            "id": doc_id,
            "content": content,
            "source": "upload",
            "scheme": None,
            "metadata": {
                "scheme_id": metadata.get("scheme_id") or doc_id,
                "scheme_name": metadata.get("scheme_name") or metadata.get("name") or doc_id,
                "category": metadata.get("category", "General"),
                "benefit_summary": metadata.get("benefit_summary", ""),
                "eligibility_summary": metadata.get("eligibility_summary", ""),
                "apply_url": metadata.get("apply_url"),
            },
        }
        self.documents.append(doc)
        self.tokenized_corpus.append(_tokenize(self._searchable_text(doc)))
        self.bm25 = BM25Okapi(self.tokenized_corpus)

        if self.chroma_collection is None:
            try:
                from app.db.chroma import get_chroma_client

                chroma = get_chroma_client()
                self.chroma_collection = chroma.collection
            except Exception:
                return

        try:
            clean_metadata = {k: str(v) for k, v in metadata.items()}
            self.chroma_collection.add(
                ids=[doc_id], documents=[content], metadatas=[clean_metadata]
            )
        except Exception as exc:
            logger.error("Failed to persist uploaded document: %s", exc)

    def add_documents_batch(self, documents: List[Dict]):
        for document in documents:
            self.add_document(
                document["id"],
                document.get("content") or document.get("text", ""),
                document.get("metadata") or {},
            )

    def clear_all(self):
        catalog_docs = [doc for doc in self.documents if doc.get("source") == "catalog"]
        self.documents = catalog_docs
        self._build_bm25_index()

    def get_stats(self) -> Dict[str, Any]:
        chroma_count = 0
        if self.chroma_collection:
            try:
                chroma_count = self.chroma_collection.count()
            except Exception:
                chroma_count = 0
        catalog_count = sum(1 for doc in self.documents if doc.get("source") == "catalog")
        return {
            "bm25_documents": len(self.documents),
            "catalog_schemes": catalog_count,
            "chromadb_documents": chroma_count,
            "has_vector_search": False,
            "mode": "catalog_bm25",
        }


_retriever: Optional[HybridRetriever] = None


def get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever


def reset_retriever():
    global _retriever
    _retriever = None
