"""
Admin Routes
=============

API endpoints for administrative operations including document ingestion,
scheme management, and analytics. All endpoints require admin JWT authentication.

Author: Jagadeep Mamidi
"""

import logging
import os
import shutil
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from pydantic import BaseModel, Field

from app.core.auth import require_admin
from app.core.config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)
settings = get_settings()

# Ensure data directories exist
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
SCHEMES_DIR = os.path.join(DATA_DIR, "schemes")
UPLOADS_DIR = os.path.join(DATA_DIR, "uploads")

for dir_path in [DATA_DIR, SCHEMES_DIR, UPLOADS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Max upload size: 10MB
MAX_UPLOAD_SIZE = 10 * 1024 * 1024


# ==================== Models ====================


class DocumentUploadResponse(BaseModel):
    success: bool = True
    document_id: str
    filename: str
    status: str
    message: str


class IngestionJob(BaseModel):
    job_id: str
    status: str
    document_count: int
    processed_count: int
    error_count: int
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    errors: List[str] = []


class SchemeCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=200)
    name_hindi: Optional[str] = None
    category: str = "General"
    scheme_type: str = "central"
    ministry: Optional[str] = None
    description: str = ""
    benefits: str = ""
    benefit_amount: Optional[str] = None
    eligibility_summary: str = ""
    application_process: Optional[str] = None
    apply_url: Optional[str] = None
    helpline: Optional[str] = None


class AnalyticsResponse(BaseModel):
    total_schemes: int
    total_sessions: int
    total_queries: int
    total_feedback: int
    queries_today: int
    top_languages: dict
    top_categories: dict


# ==================== In-memory job tracking ====================
_ingestion_jobs: dict = {}


# ==================== Endpoints ====================


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    dependencies=[Depends(require_admin)],
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    category: str = Form(default="General"),
    scheme_name: Optional[str] = Form(default=None),
):
    """Upload a document for ingestion (requires admin auth)."""

    # Validate file type
    allowed_types = {".pdf", ".txt", ".docx", ".doc", ".csv", ".json"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_types:
        raise HTTPException(
            400, f"Unsupported file type: {ext}. Allowed: {allowed_types}"
        )

    # Validate file size
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            400, f"File too large. Max size: {MAX_UPLOAD_SIZE // (1024 * 1024)}MB"
        )

    # Save file
    doc_id = str(uuid4())[:8]
    safe_filename = f"{doc_id}_{file.filename}"
    file_path = os.path.join(UPLOADS_DIR, safe_filename)

    with open(file_path, "wb") as f:
        f.write(content)

    # Create job
    job_id = str(uuid4())[:12]
    _ingestion_jobs[job_id] = {
        "job_id": job_id,
        "status": "processing",
        "document_count": 1,
        "processed_count": 0,
        "error_count": 0,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "errors": [],
    }

    # Process in background
    background_tasks.add_task(
        _process_document, job_id, file_path, category, scheme_name
    )

    return DocumentUploadResponse(
        document_id=doc_id,
        filename=file.filename,
        status="processing",
        message=f"Document queued for processing. Job ID: {job_id}",
    )


@router.get("/jobs/{job_id}", dependencies=[Depends(require_admin)])
async def get_job_status(job_id: str):
    """Get ingestion job status."""
    if job_id not in _ingestion_jobs:
        raise HTTPException(404, "Job not found")
    return _ingestion_jobs[job_id]


@router.post("/schemes", dependencies=[Depends(require_admin)])
async def create_scheme(request: SchemeCreateRequest):
    """Create a new scheme (stored in Supabase)."""
    import hashlib

    scheme_id = hashlib.md5(request.name.lower().strip().encode()).hexdigest()[:12]

    scheme_data = {
        "id": scheme_id,
        "name": request.name,
        "name_hindi": request.name_hindi or "",
        "category": request.category,
        "scheme_type": request.scheme_type,
        "ministry": request.ministry or "",
        "description": request.description,
        "benefits": request.benefits,
        "benefit_amount": request.benefit_amount or "",
        "eligibility_summary": request.eligibility_summary,
        "application_process": request.application_process or "",
        "apply_url": request.apply_url or "",
        "helpline": request.helpline or "",
        "is_active": True,
    }

    try:
        from app.db.supabase_client import get_supabase

        client = get_supabase()
        client.table("schemes").upsert(scheme_data).execute()
        logger.info(f"Created scheme: {request.name} (ID: {scheme_id})")
    except Exception as e:
        logger.warning(f"Supabase insert failed (may not be configured): {e}")

    # Also add to retriever for immediate search
    try:
        from app.rag.hybrid_retriever import get_retriever

        retriever = get_retriever()
        content = f"{request.name}. {request.description} Benefits: {request.benefits} Eligibility: {request.eligibility_summary}"
        retriever.add_document(
            doc_id=f"{scheme_id}-overview",
            content=content,
            metadata={
                "scheme_id": scheme_id,
                "scheme_name": request.name,
                "category": request.category,
                "section": "overview",
            },
        )
    except Exception as e:
        logger.warning(f"Retriever add failed: {e}")

    return {
        "success": True,
        "scheme_id": scheme_id,
        "message": f"Scheme '{request.name}' created successfully",
    }


@router.delete("/schemes/{scheme_id}", dependencies=[Depends(require_admin)])
async def delete_scheme(scheme_id: str):
    """Delete a scheme from Supabase."""
    try:
        from app.db.supabase_client import get_supabase

        client = get_supabase()
        result = client.table("schemes").delete().eq("id", scheme_id).execute()

        if not result.data:
            raise HTTPException(404, f"Scheme {scheme_id} not found")

        logger.info(f"Deleted scheme: {scheme_id}")
        return {"success": True, "message": f"Scheme {scheme_id} deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(500, f"Failed to delete scheme: {str(e)}")


@router.get(
    "/analytics",
    response_model=AnalyticsResponse,
    dependencies=[Depends(require_admin)],
)
async def get_analytics():
    """Get real analytics from database."""
    try:
        from app.db.supabase_client import get_supabase

        client = get_supabase()

        # Get counts from Supabase
        schemes = client.table("schemes").select("id", count="exact").execute()
        sessions = client.table("sessions").select("id", count="exact").execute()
        feedback = client.table("feedback").select("id", count="exact").execute()
        events = client.table("analytics_events").select("id", count="exact").execute()

        # Get today's queries
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        today_events = (
            client.table("analytics_events")
            .select("id", count="exact")
            .gte("created_at", f"{today}T00:00:00")
            .execute()
        )

        return AnalyticsResponse(
            total_schemes=schemes.count or 0,
            total_sessions=sessions.count or 0,
            total_queries=events.count or 0,
            total_feedback=feedback.count or 0,
            queries_today=today_events.count or 0,
            top_languages={},
            top_categories={},
        )

    except Exception as e:
        logger.warning(f"Analytics query failed (Supabase may not be configured): {e}")
        return AnalyticsResponse(
            total_schemes=0,
            total_sessions=0,
            total_queries=0,
            total_feedback=0,
            queries_today=0,
            top_languages={},
            top_categories={},
        )


@router.post("/reindex", dependencies=[Depends(require_admin)])
async def trigger_reindex(background_tasks: BackgroundTasks):
    """Trigger reindexing of all scheme data."""
    job_id = str(uuid4())[:12]

    _ingestion_jobs[job_id] = {
        "job_id": job_id,
        "status": "processing",
        "document_count": 0,
        "processed_count": 0,
        "error_count": 0,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "errors": [],
    }

    background_tasks.add_task(_reindex_schemes, job_id)

    return {"success": True, "job_id": job_id, "message": "Reindexing started"}


# ==================== Background Tasks ====================


async def _process_document(
    job_id: str, file_path: str, category: str, scheme_name: Optional[str]
):
    """Process an uploaded document in the background."""
    try:
        from app.pipeline.document_processor import DocumentProcessor

        processor = DocumentProcessor()
        result = await processor.process_document(
            file_path=file_path,
            filename=os.path.basename(file_path),
            metadata={
                "source": "upload",
                "category": category,
                "scheme_name": scheme_name or "Unknown",
            },
        )

        if not result.get("success"):
            raise RuntimeError(result.get("error", "Document processing failed"))

        _ingestion_jobs[job_id]["status"] = "completed"
        _ingestion_jobs[job_id]["processed_count"] = result.get("chunks_created", 1)
        _ingestion_jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()

    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        _ingestion_jobs[job_id]["status"] = "failed"
        _ingestion_jobs[job_id]["error_count"] = 1
        _ingestion_jobs[job_id]["errors"].append(str(e))
        _ingestion_jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()


async def _reindex_schemes(job_id: str):
    """Re-ingest all HuggingFace scheme datasets into ChromaDB."""
    try:
        from app.db.chroma import get_chroma_client
        from app.pipeline.ingester import get_collection_stats, ingest_all_datasets
        from app.rag.hybrid_retriever import reset_retriever

        # Clear existing ChromaDB data
        chroma = get_chroma_client()
        chroma.reset()
        reset_retriever()

        results = await ingest_all_datasets()
        total = sum(results.values())

        _ingestion_jobs[job_id]["document_count"] = total
        _ingestion_jobs[job_id]["processed_count"] = total
        _ingestion_jobs[job_id]["status"] = "completed"
        _ingestion_jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
        logger.info(f"Reindexed {total} chunks across datasets: {results}")

    except Exception as e:
        logger.error(f"Reindex failed: {e}")
        _ingestion_jobs[job_id]["status"] = "failed"
        _ingestion_jobs[job_id]["errors"].append(str(e))
        _ingestion_jobs[job_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
