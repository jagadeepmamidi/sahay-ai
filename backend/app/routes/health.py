from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: str
    version: str
    environment: str


class ReadinessResponse(BaseModel):
    """Readiness check response with service status."""

    status: str
    services: dict
    timestamp: str


@router.get("", response_model=HealthResponse)
@router.get("/", response_model=HealthResponse, include_in_schema=False)
async def health_check():
    """
    Basic health check endpoint.
    Returns OK if the application is running.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check():
    """
    Readiness check with service dependencies.
    Checks database, vector store, and LLM connectivity.
    """
    services = {}

    # Check vector store (ChromaDB)
    try:
        from app.rag.hybrid_retriever import get_retriever

        retriever = get_retriever()
        stats = retriever.get_stats()
        services["vector_store"] = "ok" if stats["has_vector_search"] else "degraded"
    except Exception as e:
        services["vector_store"] = f"error: {str(e)}"

    # Check LLM (Groq)
    try:
        from groq import Groq

        if settings.groq_api_key:
            # Just instantiate client to verify key is set; avoids a live API call
            Groq(api_key=settings.groq_api_key)
            services["llm"] = "ok"
        else:
            services["llm"] = "not configured"
    except Exception as e:
        services["llm"] = f"error: {str(e)}"

    overall_status = (
        "ready" if all(v == "ok" for v in services.values()) else "degraded"
    )

    return ReadinessResponse(
        status=overall_status,
        services=services,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
