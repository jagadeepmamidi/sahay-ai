"""
Sahay AI - Document Chunker
============================

Split documents into chunks for RAG pipeline.
Optimized for multilingual-e5-large (512 token chunks).

Author: Jagadeep Mamidi
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    sentence_endings = r'[.!?]+[\s\n]+'
    sentences = re.split(sentence_endings, text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_documents(
    documents: List[Dict[str, Any]],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> List[Dict[str, Any]]:
    """
    Split documents into smaller chunks for embedding.
    
    Args:
        documents: List of document dicts with 'text' and 'metadata'
        chunk_size: Target chunk size in characters (approximate)
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of chunk dicts with text, metadata, and chunk index
    """
    chunks = []
    
    for doc_idx, doc in enumerate(documents):
        text = doc.get("text", "")
        metadata = doc.get("metadata", {})
        
        if not text:
            continue
        
        text = clean_text(text)
        
        if len(text) <= chunk_size:
            chunks.append({
                "id": f"{doc.get('id', f'doc_{doc_idx}')}_chunk_0",
                "text": text,
                "metadata": {
                    **metadata,
                    "chunk_index": 0,
                    "source_id": doc.get("id", f"doc_{doc_idx}")
                }
            })
            continue
        
        sentences = split_into_sentences(text)
        current_chunk = ""
        chunk_idx = 0
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append({
                        "id": f"{doc.get('id', f'doc_{doc_idx}')}_chunk_{chunk_idx}",
                        "text": current_chunk.strip(),
                        "metadata": {
                            **metadata,
                            "chunk_index": chunk_idx,
                            "source_id": doc.get("id", f"doc_{doc_idx}")
                        }
                    })
                    chunk_idx += 1
                
                current_chunk = sentence
        
        if current_chunk:
            chunks.append({
                "id": f"{doc.get('id', f'doc_{doc_idx}')}_chunk_{chunk_idx}",
                "text": current_chunk.strip(),
                "metadata": {
                    **metadata,
                    "chunk_index": chunk_idx,
                    "source_id": doc.get("id", f"doc_{doc_idx}")
                }
            })
    
    logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
    return chunks


def chunk_by_scheme(
    schemes: List[Dict[str, Any]],
    fields: List[str] = None
) -> List[Dict[str, Any]]:
    """
    Chunk documents by scheme, keeping related fields together.
    
    Args:
        schemes: List of scheme dicts
        fields: Fields to include in chunks (default: name, description, eligibility, benefits)
        
    Returns:
        List of chunked documents
    """
    if fields is None:
        fields = ["name", "description", "eligibility", "benefits", "application_process"]
    
    documents = []
    
    for idx, scheme in enumerate(schemes):
        parts = []
        metadata = {"scheme_id": idx}
        
        for field in fields:
            if field in scheme and scheme[field]:
                parts.append(f"{field.replace('_', ' ').title()}: {scheme[field]}")
                metadata[field] = scheme[field]
        
        if parts:
            combined_text = " | ".join(parts)
            documents.append({
                "id": f"scheme_{idx}",
                "text": combined_text,
                "metadata": metadata
            })
    
    return chunk_documents(documents)
