# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Sahay AI is a multilingual AI platform that helps Indian citizens discover eligible government welfare schemes. It consists of a FastAPI backend and a Next.js frontend.

## Commands

### Backend

All backend commands must be run from the `backend/` directory with the venv activated.

```powershell
# Activate venv (Windows)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run data ingestion (populates ChromaDB from HuggingFace datasets)
python scripts/ingest_data.py

# Ingest a single PDF via curl
curl -X POST "http://localhost:8000/api/v1/admin/upload" -F "file=@scheme.pdf" -F "category=Agriculture" -F "scheme_name=PM-KISAN"
```

API docs (only available when `DEBUG=true`): http://localhost:8000/docs

### Frontend

Commands run from `frontend/`:

```powershell
npm install
npm run dev      # http://localhost:3000
npm run build
npm run lint
```

### Docker (full stack)

```powershell
# From repo root
docker-compose up
```

## Environment Variables

Copy `backend/.env.template` to `backend/.env`. The required keys are:

| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` | Primary LLM (`openai/gpt-oss-120b`) + Whisper STT for English |
| `SARVAM_API_KEY` | STT/TTS/Translation for Indian languages |
| `SUPABASE_URL` + `SUPABASE_ANON_KEY` | **Optional** — scheme catalog & analytics only |
| `JWT_SECRET_KEY` | Auth token signing |
| `CHROMA_PERSIST_DIR` | Path for ChromaDB storage (default: `./data/chromadb`) |
| `CORS_ORIGINS` | Comma-separated allowed origins |

Frontend: `NEXT_PUBLIC_API_URL` in `frontend/.env.local` (defaults to `http://localhost:8000/api/v1`).

> Note: The README mentions Google Gemini — this is outdated. The actual LLM is **Groq (Llama 3.3 70B)**. Supabase is entirely optional; core chat/voice/RAG works without it.

## Architecture

### Request Flow

```
User query (any language)
  → POST /api/v1/chat
  → LanguageAgent.detect_language()       # langdetect library
  → AgentOrchestrator.process()
      ├── classify_intent()               # Groq LLM → JSON intent
      ├── HybridRetriever.search()        # BM25 + ChromaDB vector search
      └── generate_response()             # Groq LLM with RAG context
  → ChatResponse (with scheme cards + suggested questions)
```

### Backend Modules (`backend/app/`)

- **`knowledge/catalog.py`** — Curated scheme records (benefits, eligibility rules, official URLs). This is the primary RAG source.
- **`agents/orchestrator.py`** — Single LLM pass. Intent is heuristic, not an extra Groq call.
- **`rag/hybrid_retriever.py`** — BM25 + alias matching over the catalog. No neural embedding on the chat path.
- **`agents/language_agent.py`** — Language detection (`langdetect`) and translation (Google Translate via `deep-translator`). Non-English → English pivot for retrieval.
- **`services/embedder.py`** — Optional, lazy-loaded, used only for admin PDF ingest.
- **`services/llm.py`** — Groq wrapper with current model fallbacks (`openai/gpt-oss-120b`).
- **`services/voice.py`** — Routes STT to Sarvam AI for Indian languages (`te`, `hi`, `ta`, `kn`, `ml`, `or`, `bn`, `mr`, `gu`, `pa`) and Groq Whisper for English. TTS is Sarvam-only.
- **`db/chroma.py`** — ChromaDB persistent client. Collection name: `sahay_schemes`, cosine similarity space. If you get a `sqlite3.OperationalError` on startup, the schema is incompatible — delete `data/chromadb/` and re-run ingestion.
- **`db/supabase_client.py`** — Optional; all callers wrap `get_supabase()` in try/except so the app degrades gracefully when unconfigured.
- **`pipeline/ingester.py`** — Ingests HuggingFace datasets or uploaded PDFs into ChromaDB via `pipeline/chunker.py` + `pipeline/document_processor.py`.
- **`core/config.py`** — `pydantic-settings` `Settings` class loaded from `backend/.env`. Use `get_settings()` (LRU-cached). `SUPPORTED_LANGUAGES` and `SCHEME_CATEGORIES` constants are also defined here.
- **`routes/`** — FastAPI routers: `chat`, `schemes`, `admin` (upload/ingest), `voice` (STT/TTS/translate), `whatsapp` (Meta webhook), `health`.

All services use the module-level singleton pattern (`_service = None` / `get_service()` function). Rate limiting is handled by `slowapi` (default 30 req/min).

### Frontend (`frontend/src/`)

- **`lib/api.ts`** — Single `fetchAPI` wrapper for all backend calls. All API functions are exported from here.
- **`app/`** — Next.js App Router pages: `/` (landing), `/chat`, `/schemes`, `/eligibility`, `/about`.
- **`components/`** — `ChatInterface`, `LanguageSelector`, `VoiceInput`, `Navbar`, `Footer`.
- **`types/index.ts`** — Shared TypeScript types.

The frontend uses Next.js 16, React 19, and Tailwind CSS v4. Turbopack is enabled in `next.config.ts`.

### Data Storage

- `data/chromadb/` — ChromaDB vector store (persistent, local)
- `data/schemes/` — Uploaded PDFs (placed here for ingestion on restart)
- ChromaDB metadata values must be strings — the code casts all metadata via `{k: str(v) for k, v in metadata.items()}` before insertion.

### WhatsApp Integration

`app/whatsapp/` handles the Meta Business API webhook at `POST /webhook/whatsapp`. Requires `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN`, and `WHATSAPP_VERIFY_TOKEN` in `.env`.
