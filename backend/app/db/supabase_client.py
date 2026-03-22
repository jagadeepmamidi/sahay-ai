"""
Supabase Client
===============

Optional Supabase client for analytics / scheme catalog storage.
The supabase package is NOT required — all core features (chat, voice, RAG)
run on ChromaDB + Groq + Sarvam without it.

If supabase is not installed or credentials are missing, every call to
get_supabase() raises RuntimeError which callers must handle gracefully
(all current callers already wrap in try/except).

Author: Jagadeep Mamidi
"""

import logging
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Guard the import — supabase is an optional dependency
try:
    from supabase import Client as SupabaseClient
    from supabase import create_client

    _SUPABASE_AVAILABLE = True
except ImportError:
    _SUPABASE_AVAILABLE = False
    SupabaseClient = None  # type: ignore[assignment,misc]
    logger.info(
        "supabase package not installed — Supabase features disabled. "
        "Core chat/voice/RAG features are unaffected."
    )

_supabase_client: Optional[object] = None


def get_supabase():
    """
    Get singleton Supabase client.

    Raises RuntimeError if:
      - supabase package is not installed, OR
      - SUPABASE_URL / SUPABASE_ANON_KEY are not configured.

    All callers should wrap this in try/except so the app degrades
    gracefully when Supabase is unavailable.
    """
    global _supabase_client

    if not _SUPABASE_AVAILABLE:
        raise RuntimeError(
            "supabase package is not installed. "
            "Run `pip install supabase` if you need Supabase features."
        )

    if _supabase_client is None:
        settings = get_settings()

        if not settings.supabase_url or not settings.supabase_anon_key:
            raise RuntimeError(
                "Supabase credentials not configured. "
                "Set SUPABASE_URL and SUPABASE_ANON_KEY in .env to enable Supabase features."
            )

        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key,
        )
        logger.info("Supabase client initialised successfully")

    return _supabase_client


def reset_client() -> None:
    """Reset the singleton (useful for testing)."""
    global _supabase_client
    _supabase_client = None
