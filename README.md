# 🙏 Sahay AI — Government Scheme Discovery Platform

<div align="center">

![Sahay AI](https://img.shields.io/badge/Sahay_AI-🙏-indigo?style=for-the-badge)
[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3-orange?style=for-the-badge)](https://groq.com/)

*AI-powered multilingual platform helping Indian citizens discover eligible government welfare schemes*

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💬 **Multilingual Chat** | Ask in Hindi, Telugu, Tamil, Bengali, or 11+ Indian languages |
| 🎙️ **Voice Input/Output** | Speak your question and hear answers — powered by Sarvam AI |
| 🔍 **Scheme Discovery** | Browse 500+ government schemes with category filters |
| ✅ **Eligibility Check** | Describe your situation to find matching schemes |
| 🤖 **AI-Powered RAG** | Groq (Llama 3.3 70B) + hybrid BM25/vector search for accurate results |
| 📱 **WhatsApp Bot** | Discover schemes via WhatsApp with voice message support |
| 📄 **Document Upload** | Add scheme PDFs to expand the knowledge base |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- API Keys: [Groq](https://console.groq.com/) (LLM) + [Sarvam AI](https://www.sarvam.ai/) (Indian language STT/TTS)

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt

copy .env.template .env      # then edit .env with your API keys
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev                  # http://localhost:3000
```

### 3. Docker (full stack)

```bash
docker-compose up
```

**API docs** (when `DEBUG=true`): http://localhost:8000/docs

---

## 🏗️ Architecture

```
sahay-ai/
├── backend/                # FastAPI Python backend
│   ├── app/
│   │   ├── agents/         # AI orchestrator, language agent
│   │   ├── rag/            # Hybrid retriever (BM25 + ChromaDB)
│   │   ├── routes/         # API: chat, schemes, voice, whatsapp
│   │   ├── services/       # LLM, embedder, voice (Sarvam/Groq)
│   │   ├── pipeline/       # Document ingestion & chunking
│   │   └── core/           # Settings, config
│   ├── scripts/            # Data ingestion scripts
│   └── requirements.txt
├── frontend/               # Next.js 16 React frontend
│   └── src/
│       ├── app/            # Pages: /, /chat, /schemes, /about
│       ├── components/     # ChatInterface, VoiceInput, LanguageSelector
│       └── lib/            # API client
├── data/                   # ChromaDB vector store, uploaded PDFs
└── docker-compose.yml
```

### Request Flow

```
User query (any language)
  → POST /api/v1/chat
  → LanguageAgent.detect_language()
  → AgentOrchestrator.process()
      ├── classify_intent()              # Groq LLM → JSON intent
      ├── HybridRetriever.search()       # BM25 + ChromaDB vector search
      └── generate_response()            # Groq LLM with RAG context
  → ChatResponse (scheme cards + suggested questions)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **LLM** | Groq (Llama 3.3 70B) |
| **Embeddings** | intfloat/multilingual-e5-large (1024d) |
| **STT/TTS** | Sarvam AI (Indian languages) + Groq Whisper (English) |
| **Backend** | FastAPI, Python 3.11 |
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS v4 |
| **Vector DB** | ChromaDB (persistent, local) |
| **Database** | Supabase PostgreSQL (optional — scheme catalog & analytics) |
| **Translation** | deep-translator (Google Translate) |
| **Rate Limiting** | slowapi (30 req/min) |

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Send message to AI |
| `/api/v1/schemes` | GET | List schemes (paginated, filterable) |
| `/api/v1/schemes/{id}` | GET | Scheme details |
| `/api/v1/voice/transcribe` | POST | Speech-to-text |
| `/api/v1/voice/speak` | POST | Text-to-speech |
| `/api/v1/admin/upload` | POST | Upload scheme PDF |
| `/webhook/whatsapp` | POST | WhatsApp Business webhook |

---

## 📱 Supported Languages

🇬🇧 English · 🇮🇳 Hindi (हिंदी) · Telugu (తెలుగు) · Tamil (தமிழ்) · Bengali (বাংলা) · Marathi (मराठी) · Gujarati (ગુજરાતી) · Kannada (ಕನ್ನಡ) · Malayalam (മലയാളം) · Punjabi (ਪੰਜਾਬੀ) · Odia (ଓଡ଼ିଆ)

---

## ⚙️ Environment Variables

Copy `backend/.env.template` to `backend/.env`. Required keys:

| Variable | Purpose |
|----------|---------|
| `GROQ_API_KEY` | LLM (Llama 3.3 70B) + Whisper STT for English |
| `SARVAM_API_KEY` | STT/TTS/Translation for Indian languages |
| `JWT_SECRET_KEY` | Auth token signing |

Optional:

| Variable | Purpose |
|----------|---------|
| `SUPABASE_URL` + `SUPABASE_ANON_KEY` | Scheme catalog & analytics |
| `WHATSAPP_PHONE_NUMBER_ID` / `ACCESS_TOKEN` / `VERIFY_TOKEN` | WhatsApp integration |
| `CHROMA_PERSIST_DIR` | ChromaDB path (default: `./data/chromadb`) |
| `CORS_ORIGINS` | Allowed origins |

Frontend: `NEXT_PUBLIC_API_URL` in `frontend/.env.local` (default: `http://localhost:8000/api/v1`)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**🙏 Built with ❤️ for Indian Citizens**

*Making government schemes accessible to everyone*

</div>
