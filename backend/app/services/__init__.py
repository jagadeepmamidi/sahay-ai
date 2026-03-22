"""
Sahay AI - Services Package
============================

Lazy imports — import directly from the submodule you need:

    from app.services.embedder import get_embedder
    from app.services.voice import get_voice_service
    from app.services.llm import get_llm_service

Eager top-level imports are intentionally avoided here so that running
the ingest script (which only needs the embedder) does not force-load
groq / sarvamai / sentence-transformers all at once.
"""
