"""
Sahay AI - FastAPI Application Entry Point
==========================================

Main application with API versioning, middleware, and route registration.

Author: Jagadeep Mamidi
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.routes import admin, chat, health, schemes, voice, whatsapp

# Setup rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{get_settings().rate_limit_per_minute}/minute"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Using model: {settings.groq_chat_model}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
    ## Sahay AI - Government Scheme Discovery Platform

    A conversational AI agent to help citizens discover eligible government schemes.

    ### Features:
    - **Multilingual Chat**: Ask questions in Hindi, Telugu, Tamil, and more (11+ languages)
    - **Verified Information**: Data sourced from official government portals
    - **Scheme Discovery**: Find schemes based on eligibility criteria
    - **Document Processing**: Upload scheme documents for ingestion

    ### API Sections:
    - `/api/v1/chat` - Chat with Sahay AI
    - `/api/v1/schemes` - Browse and search schemes
    - `/api/v1/admin` - Admin operations for data ingestion
    - `/api/v1/voice` - Speech-to-text and text-to-speech
    - `/webhook/whatsapp` - WhatsApp webhook
    """,
    version=settings.app_version,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers."""
    start_time = datetime.now()
    response = await call_next(request)
    process_time = (datetime.now() - start_time).total_seconds()
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred",
        },
    )


# Register routers with API version prefix
API_V1_PREFIX = "/api/v1"

app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(chat.router, prefix=f"{API_V1_PREFIX}/chat", tags=["Chat"])
app.include_router(schemes.router, prefix=f"{API_V1_PREFIX}/schemes", tags=["Schemes"])
app.include_router(admin.router, prefix=f"{API_V1_PREFIX}/admin", tags=["Admin"])
app.include_router(voice.router, prefix=f"{API_V1_PREFIX}/voice", tags=["Voice"])
app.include_router(whatsapp.router, prefix="", tags=["WhatsApp"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "description": "Professional Government Scheme Discovery Platform (11 languages supported)",
        "docs": "/docs" if settings.debug else "Disabled in production",
        "health": "/health",
        "api_prefix": API_V1_PREFIX,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.debug)
