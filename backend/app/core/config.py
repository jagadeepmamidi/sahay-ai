"""
Sahay AI - Core Configuration
=============================

Centralized configuration management using Pydantic Settings.
All environment variables are validated and typed here.

Author: Jagadeep Mamidi
"""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Sahay AI"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"

    # Groq API (primary LLM - free tier)
    groq_api_key: str = ""
    groq_chat_model: str = "llama-3.3-70b-versatile"
    groq_whisper_model: str = "whisper-large-v3"

    # Sarvam AI (Indian languages STT/TTS/Translation)
    sarvam_api_key: str = ""
    sarvam_stt_model: str = "saarika:v2"
    sarvam_tts_model: str = "bulbul:v2"
    sarvam_translate_model: str = "mayura:v1"

    # Supabase (optional — only needed for scheme catalog / analytics features)
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # CORS
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins into a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # JWT Auth
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Vector Database - ChromaDB (local, persistent, free)
    chroma_persist_dir: str = Field(
        default="data/chromadb",
        validation_alias=AliasChoices("CHROMA_PERSIST_DIR", "CHROMA_PERSIST_DIRECTORY"),
    )
    embedding_model: str = Field(
        default="intfloat/multilingual-e5-large",
        validation_alias=AliasChoices("EMBEDDING_MODEL"),
    )
    embedding_dimension: int = 1024

    # Multilingual
    default_language: str = "en"
    enable_translation: bool = True

    # Rate Limiting
    rate_limit_per_minute: int = 30
    cache_ttl_seconds: int = 3600

    # WhatsApp (Meta Business API)
    whatsapp_phone_number_id: str = ""
    whatsapp_business_account_id: str = ""
    whatsapp_access_token: str = ""
    whatsapp_verify_token: str = "change-me"
    whatsapp_graph_api_version: str = "v21.0"

    # WhatsApp Cloud API URL
    @property
    def whatsapp_api_url(self) -> str:
        return f"https://graph.facebook.com/{self.whatsapp_graph_api_version}"

    @property
    def chroma_persist_path(self) -> str:
        """Return an absolute Chroma persistence path."""
        persist_path = Path(self.chroma_persist_dir).expanduser()
        if not persist_path.is_absolute():
            persist_path = BACKEND_DIR / persist_path
        return str(persist_path.resolve())


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    This function is cached to avoid reading .env file multiple times.
    """
    return Settings()


# Supported languages with their names
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi (हिंदी)",
    "te": "Telugu (తెలుగు)",
    "ta": "Tamil (தமிழ்)",
    "bn": "Bengali (বাংলা)",
    "mr": "Marathi (मराठी)",
    "gu": "Gujarati (ગુજરાતી)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "ml": "Malayalam (മലയാളം)",
    "pa": "Punjabi (ਪੰਜਾਬੀ)",
    "or": "Odia (ଓଡ଼ିଆ)",
}

# Scheme categories for filtering
SCHEME_CATEGORIES = [
    "Agriculture",
    "Education",
    "Health",
    "Housing",
    "Women & Child",
    "Social Welfare",
    "Employment",
    "Business & Entrepreneurship",
    "Financial Inclusion",
    "Rural Development",
    "Urban Development",
    "Skills & Training",
]

# Indian States and UTs
INDIAN_STATES = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry",
]
