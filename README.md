# 🙏 Sahay AI - Government Scheme Discovery Platform

<div align="center">

![Sahay AI](https://img.shields.io/badge/Sahay_AI-🙏-indigo?style=for-the-badge)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-2.0-blue?style=for-the-badge&logo=google)](https://ai.google.dev/)

*AI-powered platform helping Indian citizens discover eligible government schemes*

</div>

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Google Gemini API Key (free at [Google AI Studio](https://aistudio.google.com/app/apikey))

### 1. Clone & Setup

```bash
cd sahay-ai

# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Create .env file
copy .env.template .env
# Edit .env and add your GOOGLE_API_KEY
```

### 2. Run Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

### 4. Open in Browser

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 💬 **Multilingual Chat** | Ask in Hindi, Telugu, Tamil, or 11+ Indian languages |
| 🔍 **Scheme Discovery** | Browse 100+ government schemes with filters |
| ✅ **Eligibility Check** | Enter profile details to find matching schemes |
| 🤖 **AI-Powered** | Google Gemini 2.0 for intelligent responses |
| 🗄️ **Hybrid RAG** | BM25 + Vector search for accurate retrieval |
| 📄 **Document Upload** | Add scheme PDFs to expand knowledge base |

---

## 🏗️ Architecture

```
sahay-ai/
├── backend/              # FastAPI Python backend
│   ├── app/
│   │   ├── agents/       # AI orchestrator, language agent
│   │   ├── rag/          # Hybrid retriever (BM25 + Vector)
│   │   ├── routes/       # API endpoints
│   │   ├── pipeline/     # Document ingestion
│   │   └── core/         # Configuration
│   └── requirements.txt
├── frontend/             # Next.js 14 React frontend
│   └── src/
│       ├── app/          # Pages (chat, schemes, eligibility)
│       ├── components/   # UI components
│       └── lib/          # API client
├── data/                 # Vector DB, schemes, uploads
└── docker-compose.yml    # Docker configuration
```

---

## 🛠️ Tech Stack

- **LLM**: Google Gemini 2.0 Flash (free tier)
- **Backend**: FastAPI, Python 3.11
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Vector DB**: ChromaDB
- **Database**: Supabase (PostgreSQL)
- **Translation**: deep-translator (Google Translate)

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Send message to AI |
| `/api/v1/schemes` | GET | List all schemes |
| `/api/v1/schemes/{id}` | GET | Scheme details |
| `/api/v1/schemes/eligibility` | POST | Check eligibility |
| `/api/v1/admin/upload` | POST | Upload scheme document |

---

## 📱 Supported Languages

🇬🇧 English • 🇮🇳 Hindi (हिंदी) • Telugu (తెలుగు) • Tamil (தமிழ்) • Bengali (বাংলা) • Marathi (मराठी) • Gujarati (ગુજરાતી) • Kannada (ಕನ್ನಡ) • Malayalam (മലയാളം) • Punjabi (ਪੰਜਾਬੀ) • Odia (ଓଡ଼ିଆ)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

<div align="center">

**🙏 Built with ❤️ for Indian Citizens**

*Making government schemes accessible to everyone*

</div>
