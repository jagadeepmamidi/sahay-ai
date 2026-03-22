SAHAY AI
Implementation Plan  —  v2.0
Multilingual Government Scheme Discovery Platform

Updated: March 21, 2026  |  Telugu · Hindi · English

What Changed from v1.0

⚠️  6 issues from the original plan have been fixed in this version. Read these before starting.

#	Issue	Old Approach	Fixed Approach
1	Telugu STT quality	Groq Whisper (poor Telugu)	Sarvam AI STT (11 Indian languages)
2	TTS for responses	pyttsx3 offline (no Telugu voice)	Sarvam TTS / Google TTS Neural2
3	Embedding model	MiniLM-L12 384d (weak multilingual)	multilingual-e5-large 1024d
4	Vector DB	Pinecone free (1GB — too tight)	ChromaDB local (no limits, fully free)
5	Backend hosting	Railway (no free tier since 2024)	Render free tier (750 hrs/month)
6	WhatsApp webhook bug	hub.mode as param name — invalid FastAPI	Correct alias= Query params + PlainTextResponse

1. Project Overview
An AI-powered multilingual chatbot helping Indian citizens discover and understand government welfare schemes through voice and text in their preferred language.

Key Features
•	Voice input in Indian languages (Telugu, Hindi) via Sarvam AI STT
•	WhatsApp chatbot integration via Meta Business API
•	Hybrid RAG pipeline — BM25 keyword + ChromaDB vector + reranker
•	Eligibility checking and application guidance
•	Response translated back to user's language via Sarvam Translate

Language Priority
Priority	Language	Script	STT Support
1 — Primary	Telugu	తెలుగు	Sarvam AI (native)
2 — Secondary	Hindi	हिंदी	Sarvam AI (native)
3 — Tertiary	English	Latin	Groq Whisper
4 — Future	Tamil, Kannada, Odia…	Various	Sarvam AI

2. Tech Stack
Component	Choice	Reason	Cost
LLM	Groq — Llama 3.3 70B	Fast inference, free tier	$0
STT (Indian langs)	Sarvam AI saarika-v2	Native Telugu/Hindi, free tier	$0
STT (English fallback)	Groq Whisper large-v3	Fast, free tier	$0
TTS	Sarvam AI bulbul-v2	Indian language voices, free tier	$0
Vector DB	ChromaDB (local, persistent)	No limits, no API key, fully free	$0
Embeddings	multilingual-e5-large (1024d)	Strong multilingual recall	$0
Translation	Sarvam Translate API	Indian language pairs, free tier	$0
SQL DB	Supabase (existing)	Already set up	$0
Frontend	Next.js 14 + TypeScript	App Router, Vercel-optimised	$0
Backend	FastAPI + Python 3.11	Async, fast, easy to deploy	$0
Frontend Deploy	Vercel	Free, auto-deploy on push	$0
Backend Deploy	Render free tier	750 hrs/month free	$0
WhatsApp	Meta Business API	Free messaging (limited)	$0

3. Data Sources
Primary Dataset
✅  shrijayan/gov_myscheme on HuggingFace — 723 PDFs from MyScheme portal. Contains scheme name, eligibility, benefits, application process. Available in Parquet/JSON/CSV.

Dataset	Source	Use Case
gov_myscheme (723 PDFs)	shrijayan / HuggingFace	Primary scheme data — eligibility, benefits, process
indian-govt-scholarships	NetraVerse / HuggingFace	Scholarship Q&A pairs
scholarship_dataset	vyshnaviprasad / HuggingFace	Andhra Pradesh state scholarships
Governance Translation	coild-aikosh / HuggingFace	Hindi ↔ Telugu translation pairs
PMIndiaSum	PMIndiaData / HuggingFace	Multilingual summaries of PM schemes

4. Architecture
Updated Data Flow
💡  Key change from v1: queries are embedded in their original language using multilingual-e5-large, then retrieved directly from ChromaDB — no translate-first bottleneck. Translation happens only at the final LLM prompt stage.

Step	Action	Service
1	User sends voice/text via WhatsApp or Web	Meta API / Next.js
2	Detect language (auto)	Sarvam API / langdetect
3	If voice: transcribe audio	Sarvam saarika-v2 (Indian) / Groq Whisper (EN)
4	Embed query in original language	multilingual-e5-large (local)
5	Hybrid retrieval: BM25 + ChromaDB vector search	BM25s + ChromaDB (local)
6	Rerank top-k results	cross-encoder/ms-marco-MiniLM-L-6-v2
7	Translate context + query to English for LLM	Sarvam Translate
8	Generate response	Groq Llama 3.3 70B
9	Translate response back to user's language	Sarvam Translate
10	Deliver via same channel + optional TTS	Meta API / Sarvam bulbul-v2

5. Implementation Phases

Phase 1: Foundation & STT Setup  —  Week 1

Tasks
	☐  1.1 — Create Groq account → get API key (https://console.groq.com/)
	☐  1.2 — Create Sarvam AI account → get API key (https://dashboard.sarvam.ai/)
	☐  1.3 — Update backend dependencies

# requirements.txt — add these
groq>=1.0.0
sarvamai>=1.0.0            # Sarvam AI Python SDK
chromadb>=0.5.0
sentence-transformers>=3.0.0
rank-bm25>=0.2.2
langdetect>=1.0.9
tenacity>=8.0.0            # retry with backoff

	☐  1.4 — Update config

# backend/app/core/config.py
groq_api_key: str = ""
groq_chat_model: str = "llama-3.3-70b-versatile"
groq_whisper_model: str = "whisper-large-v3"  # English fallback only

sarvam_api_key: str = ""                     # replaces Groq for Indian STT/TTS
sarvam_stt_model: str = "saarika:v2"
sarvam_tts_model: str = "bulbul:v2"
sarvam_translate_model: str = "mayura:v1"

chroma_persist_dir: str = "./data/chroma"    # local persistent storage
embedding_model: str = "intfloat/multilingual-e5-large"

	☐  1.5 — Set up ChromaDB client

# backend/app/db/chroma.py
import chromadb
from chromadb.config import Settings

class ChromaDB:
    def __init__(self, persist_dir: str = './data/chroma'):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name='sahay_schemes',
            metadata={'hnsw:space': 'cosine'}
        )

    def upsert(self, ids, embeddings, documents, metadatas):
        self.collection.upsert(
            ids=ids, embeddings=embeddings,
            documents=documents, metadatas=metadatas
        )

    def query(self, embedding, n_results=10, where=None):
        return self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            where=where,
            include=['documents', 'metadatas', 'distances']
        )

Phase 2: Data Ingestion Pipeline  —  Week 1–2

Tasks
	☐  2.1 — Download MyScheme dataset from HuggingFace
	☐  2.2 — Create pipeline structure

backend/app/pipeline/
├── data_loader.py        # HuggingFace dataset download
├── pdf_processor.py      # PDF text extraction (pypdf2)
├── chunker.py            # 512-token chunks, 50-token overlap
├── embedder.py           # multilingual-e5-large embeddings
└── chroma_ingester.py    # ChromaDB upsert

	☐  2.3 — Embed and ingest — dimension: 1024 (multilingual-e5-large)

# backend/app/pipeline/embedder.py
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('intfloat/multilingual-e5-large')
# 1024 dimensions — much better multilingual recall than MiniLM 384d

def embed(texts: list[str]) -> list[list[float]]:
    # e5 models require 'passage: ' prefix for documents
    prefixed = [f'passage: {t}' for t in texts]
    return model.encode(prefixed, normalize_embeddings=True).tolist()

def embed_query(query: str) -> list[float]:
    # 'query: ' prefix for user queries
    return model.encode(f'query: {query}', normalize_embeddings=True).tolist()

Phase 3: Voice Integration — Sarvam AI  —  Week 2

⚠️  Use Sarvam saarika-v2 for Telugu and Hindi. Fall back to Groq Whisper only for English. Never use Groq Whisper as primary for Indian languages — quality is poor.

Tasks
	☐  3.1 — Create voice service with Sarvam + Groq fallback

# backend/app/services/voice.py
import httpx, base64
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential

SARVAM_STT_URL = 'https://api.sarvam.ai/speech-to-text'
INDIAN_LANGS = {'te', 'hi', 'ta', 'kn', 'ml', 'or', 'bn', 'mr', 'gu', 'pa'}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def transcribe_audio(audio_bytes: bytes, language: str = None) -> str:
    if language in INDIAN_LANGS or language is None:
        # Sarvam for Indian languages
        async with httpx.AsyncClient() as client:
            r = await client.post(
                SARVAM_STT_URL,
                headers={'api-subscription-key': SARVAM_API_KEY},
                json={
                    'audio': base64.b64encode(audio_bytes).decode(),
                    'language_code': language or 'unknown',
                    'model': 'saarika:v2',
                }
            )
        return r.json()['transcript']
    else:
        # Groq Whisper for English
        client = Groq()
        result = client.audio.transcriptions.create(
            file=('audio.webm', audio_bytes),
            model='whisper-large-v3',
            response_format='text'
        )
        return result.text

	☐  3.2 — Create TTS service using Sarvam bulbul-v2
	☐  3.3 — Build VoiceInput.tsx frontend component (MediaRecorder API)
	☐  3.4 — Add language detection (auto-detect on text using langdetect)

Phase 4: WhatsApp Integration (Fixed)  —  Week 2–3

🐛  The original webhook code had a FastAPI bug — parameter names with dots are invalid Python. The fix is to use alias= in Query(). Also the challenge response must be PlainTextResponse, not int.

Tasks
	☐  4.1 — Create Meta Business App at developers.facebook.com
	☐  4.2 — Create WhatsApp webhook — fixed code below

# backend/app/routes/whatsapp.py — CORRECTED
from fastapi import APIRouter, Request, Query
from fastapi.responses import PlainTextResponse
import os

router = APIRouter(prefix='/webhook/whatsapp', tags=['whatsapp'])
VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN')

@router.get('/')
async def verify_webhook(
    hub_mode: str = Query(..., alias='hub.mode'),
    hub_verify_token: str = Query(..., alias='hub.verify_token'),
    hub_challenge: str = Query(..., alias='hub.challenge'),
):
    if hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)   # must be plain text
    return PlainTextResponse('Forbidden', status_code=403)

@router.post('/')
async def handle_message(request: Request):
    data = await request.json()
    # process incoming message...

	☐  4.3 — Update Graph API version to v21.0 (v18.0 is outdated)

# backend/app/whatsapp/client.py
GRAPH_API_VERSION = 'v21.0'   # was v18.0 — update this
BASE_URL = f'https://graph.facebook.com/{GRAPH_API_VERSION}'

	☐  4.4 — Add tenacity retry to all Groq calls (rate limit safety)

# Wrap every Groq API call with this decorator
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type(groq.RateLimitError),
)
async def call_llm(prompt: str) -> str:
    ...

	☐  4.5 — Create WhatsApp message handler and session manager

Phase 5: Frontend Enhancement  —  Week 3

Tasks
	☐  5.1 — Language selector component (Telugu / Hindi / English)
	☐  5.2 — Voice input button with recording state indicator
	☐  5.3 — Audio playback for TTS responses
	☐  5.4 — Settings panel — language preference, voice toggle
	☐  5.5 — WhatsApp deep-link button on landing page

Phase 6: Deployment (Render, not Railway)  —  Week 3–4

📌  Railway removed its free tier. Use Render instead — 750 hours/month free, spins down after 15 min idle (acceptable for demo). Backend URL changes from railway.app to onrender.com.

Render setup
# render.yaml (add to backend root)
services:
  - type: web
    name: sahay-api
    env: python
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GROQ_API_KEY
        sync: false
      - key: SARVAM_API_KEY
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_ROLE_KEY
        sync: false
      - key: WHATSAPP_VERIFY_TOKEN
        sync: false
      - key: WHATSAPP_ACCESS_TOKEN
        sync: false

Frontend env (Vercel) — updated URL
# frontend/.env.local
NEXT_PUBLIC_API_URL=https://sahay-api.onrender.com/api/v1  # was railway.app
NEXT_PUBLIC_WHATSAPP_ENABLED=true

Deployment Checklist
	☐  Deploy backend to Render — connect GitHub, set env vars
	☐  Deploy frontend to Vercel — connect GitHub, set NEXT_PUBLIC_API_URL
	☐  Update CORS to allow sahay-ai.vercel.app
	☐  Ingest ChromaDB data on Render (run ingest script post-deploy)
	☐  Configure WhatsApp webhook to Render URL
	☐  Test end-to-end with test WhatsApp numbers
	☐  Submit Meta Business verification

6. Database Setup
ChromaDB Index Schema
# Collection: sahay_schemes
# Embedding dimension: 1024 (multilingual-e5-large)
# Distance metric: cosine

# Metadata per chunk:
{
    'scheme_name': str,
    'category': str,            # agriculture, health, education…
    'language': str,            # source language: 'en', 'hi', 'te'
    'source_url': str,
    'eligibility_criteria': str,
    'benefits': str,
    'application_process': str,
    'chunk_index': int,
}

Supabase — New WhatsApp Tables
-- whatsapp_sessions
CREATE TABLE whatsapp_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  phone_number VARCHAR(20) UNIQUE NOT NULL,
  language_preference VARCHAR(10) DEFAULT 'te',
  created_at TIMESTAMP DEFAULT NOW(),
  last_interaction TIMESTAMP DEFAULT NOW()
);

-- whatsapp_messages
CREATE TABLE whatsapp_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES whatsapp_sessions(id),
  direction VARCHAR(10),    -- 'inbound' or 'outbound'
  message_type VARCHAR(20), -- 'text', 'audio', 'image'
  content TEXT,
  transcription TEXT,
  translation TEXT,
  response TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

7. Timeline
Week	Days	Tasks
Week 1	Day 1–2	Groq + Sarvam API keys, update config, ChromaDB setup
Week 1	Day 3–4	Data download, embedding pipeline (multilingual-e5-large)
Week 1	Day 5	Ingest 723 scheme PDFs into ChromaDB
Week 2	Day 6–7	Sarvam STT/TTS service, VoiceInput component
Week 2	Day 8–9	WhatsApp webhook (fixed), message handler
Week 2	Day 10	Hybrid RAG — BM25 + ChromaDB + reranker
Week 3	Day 11–13	Frontend polish — language selector, voice UI, WhatsApp link
Week 3	Day 14–15	CORS, Render deploy, Vercel deploy
Week 4	Day 16–17	WhatsApp webhook verification on Render
Week 4	Day 18–20	End-to-end testing (Telugu voice → scheme → reply)

8. Budget
Service	Free Tier	Limits	Monthly Cost
Groq API	✓	30 RPM / 14,400 req/day	$0
Sarvam AI	✓	1,000 min STT + 10,000 chars TTS/month	$0
ChromaDB	✓ (local)	No limits — runs on Render instance	$0
Supabase	✓	500MB database	$0
Vercel	✓	100GB bandwidth	$0
Render	✓	750 hrs/month (spins down after 15 min idle)	$0
Meta WhatsApp	✓	1,000 free conversations/month	$0

✅  Total monthly cost: $0 for demo scale. If Sarvam free tier exhausted, Groq Whisper handles English and Sarvam stays for Indian languages only, stretching the free quota further.

9. Environment Variables
# backend/.env

# Groq (https://console.groq.com/)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxx

# Sarvam AI (https://dashboard.sarvam.ai/)  ← Official dashboard
SARVAM_API_KEY=xxxxxxxxxxxxxxx

# Meta WhatsApp (https://developers.facebook.com/)
WHATSAPP_PHONE_NUMBER_ID=xxxxxxxxxxxxxx
WHATSAPP_BUSINESS_ACCOUNT_ID=xxxxxxxxxxxxxx
WHATSAPP_ACCESS_TOKEN=EAAAZxxxxxxxxxxxxx
WHATSAPP_VERIFY_TOKEN=your_secure_token

# Supabase (existing)
SUPABASE_URL=https://xxxxxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJxxxxxxxxxxxxx

# ChromaDB (local path — no API key needed)  ← NEW
CHROMA_PERSIST_DIR=./data/chroma

10. Troubleshooting
Issue	Likely Cause	Fix
Sarvam STT returns empty transcript	Audio not WAV/PCM format	Convert WebM → WAV before sending: use ffmpeg or soundfile
ChromaDB collection not found	persist_dir path mismatch between ingest and server	Use absolute path or env var for CHROMA_PERSIST_DIR
multilingual-e5-large OOM on Render	Free Render instance is 512MB RAM	Use smaller model: paraphrase-multilingual-mpnet-base-v2 (768d)
WhatsApp webhook 403	VERIFY_TOKEN mismatch	Ensure token in Meta dashboard == WHATSAPP_VERIFY_TOKEN env var
Groq rate limit hit	Burst of WhatsApp messages	tenacity retry already handles — check retry logs
Response in wrong language	Translation step skipped on short inputs	Always run language detection even on 1-word inputs
Render backend cold start	Spins down after 15 min idle	Add /health endpoint, use UptimeRobot ping every 10 min (free)
Sarvam STT returns empty transcript	Audio format issue or API key problem	Check dashboard.sarvam.ai for API key and quota
Sarvam 401 Unauthorized	Invalid or expired API key	Get fresh key from https://dashboard.sarvam.ai/
Sarvam package import error	SDK not installed	Run: pip install sarvamai

12. Useful Links

| Service | URL |
|---------|-----|
| Groq Console | https://console.groq.com/ |
| Sarvam Dashboard | https://dashboard.sarvam.ai/ |
| Sarvam Docs | https://docs.sarvam.ai/ |
| Meta for Developers | https://developers.facebook.com/ |
| Vercel | https://vercel.com/ |
| Render | https://render.com/ |

13. Testing Checklist
Voice & STT
	☐  Telugu voice input transcribes correctly via Sarvam
	☐  Hindi voice input transcribes correctly via Sarvam
	☐  English voice falls back to Groq Whisper
	☐  Audio format (WebM) converts correctly before Sarvam
RAG Pipeline
	☐  BM25 keyword search returns relevant schemes
	☐  ChromaDB vector search returns semantically similar chunks
	☐  Reranker correctly prioritises most relevant results
	☐  Telugu query retrieves English scheme docs correctly
WhatsApp
	☐  Webhook verification succeeds (GET /webhook/whatsapp)
	☐  Text messages received and processed
	☐  Audio messages transcribed via Sarvam
	☐  Responses sent back with correct language
	☐  Session state persists across messages
End-to-End
	☐  User sends Telugu voice → scheme found → reply in Telugu
	☐  User sends Hindi text → eligibility check → reply in Hindi
	☐  Error cases handled gracefully (no matching scheme)
	☐  Rate limit recovery works without user-visible failure

Sahay AI — Implementation Plan v2.0  |  March 21, 2026
