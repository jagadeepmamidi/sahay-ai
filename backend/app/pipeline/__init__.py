"""
Sahay AI Pipeline Package
=========================

Data loading, processing, and ingestion pipeline for scheme data.

Avoid eager imports here so the API can still start even if optional
ingestion-only dependencies such as `datasets` are not installed yet.
"""

__all__ = [
    "load_huggingface_dataset",
    "dataset_to_documents",
    "chunk_documents",
    "ingest_documents",
]
