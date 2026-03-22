"""
Sahay AI - Document Ingester
=============================

Ingest documents into ChromaDB with embeddings.

Author: Jagadeep Mamidi
"""

import logging
from typing import Any, Dict, List

from app.db.chroma import ChromaDBClient, get_chroma_client
from app.services.embedder import get_embedder

logger = logging.getLogger(__name__)


async def ingest_documents(
    documents: List[Dict[str, Any]], batch_size: int = 32, show_progress: bool = True
) -> int:
    """
    Ingest documents into ChromaDB with embeddings.

    Args:
        documents: List of document dicts with 'text' and 'metadata'
        batch_size: Number of documents per embedding batch
        show_progress: Show progress bar

    Returns:
        Number of chunks ingested
    """
    from app.pipeline.chunker import chunk_documents

    logger.info(f"Starting ingestion of {len(documents)} documents")

    chroma = get_chroma_client()
    embedder = get_embedder()

    chunks = chunk_documents(documents)
    logger.info(f"Created {len(chunks)} chunks")

    ids = []
    embeddings = []
    texts = []
    metadatas = []

    total_chunks = len(chunks)

    for i in range(0, total_chunks, batch_size):
        batch = chunks[i : i + batch_size]

        texts_batch = [chunk["text"] for chunk in batch]
        embeddings_batch = embedder.embed_documents(texts_batch)

        for j, chunk in enumerate(batch):
            ids.append(chunk["id"])
            embeddings.append(embeddings_batch[j])
            texts.append(chunk["text"])
            metadatas.append(chunk["metadata"])

        if show_progress:
            logger.info(
                f"Processed {min(i + batch_size, total_chunks)}/{total_chunks} chunks"
            )

    chroma.upsert(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)

    logger.info(f"Successfully ingested {len(chunks)} chunks into ChromaDB")
    return len(chunks)


async def ingest_huggingface_dataset(
    dataset_name: str = "gov_myscheme", batch_size: int = 32
) -> int:
    """
    Load and ingest a HuggingFace dataset directly.

    Args:
        dataset_name: Name of the dataset
        batch_size: Batch size for embedding

    Returns:
        Number of chunks ingested
    """
    from app.pipeline.data_loader import dataset_to_documents, load_huggingface_dataset

    logger.info(f"Loading dataset: {dataset_name}")
    dataset = load_huggingface_dataset(dataset_name)

    documents = dataset_to_documents(dataset, source_name=dataset_name)
    logger.info(f"Converted {len(documents)} documents")

    return await ingest_documents(documents, batch_size=batch_size)


async def ingest_all_datasets(batch_size: int = 32) -> Dict[str, int]:
    """
    Load and ingest all available datasets.

    Args:
        batch_size: Batch size for embedding

    Returns:
        Dict mapping dataset name to number of chunks ingested
    """
    from app.pipeline.data_loader import dataset_to_documents, get_all_datasets

    all_datasets = get_all_datasets()
    results = {}

    for name, dataset in all_datasets.items():
        try:
            documents = dataset_to_documents(dataset, source_name=name)
            count = await ingest_documents(documents, batch_size=batch_size)
            results[name] = count
        except Exception as e:
            logger.error(f"Failed to ingest {name}: {e}")
            results[name] = 0

    return results


async def reindex_collection() -> int:
    """
    Clear and rebuild the entire ChromaDB collection.

    Returns:
        Number of chunks reindexed
    """
    chroma = get_chroma_client()

    logger.info("Resetting ChromaDB collection")
    chroma.reset()

    return await ingest_all_datasets()


def get_collection_stats() -> Dict[str, Any]:
    """
    Get statistics about the ChromaDB collection.

    Returns:
        Dict with collection stats
    """
    chroma = get_chroma_client()

    total_count = chroma.count()
    sample = chroma.peek(limit=5)

    return {
        "total_chunks": total_count,
        "sample_documents": len(sample.get("documents", [])),
        "persist_directory": chroma.persist_dir,
        "collection_name": chroma.collection_name,
    }
