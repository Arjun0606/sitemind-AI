# 🏗️ SiteMind - The AI Site Engineer

> "Fleetline for Construction" - Give site engineers superpowers with AI

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

## 🎯 What is SiteMind?

SiteMind is an AI-powered assistant for construction site engineers in India. It lives in WhatsApp and can:

- 📐 **Read Blueprints** - Powered by Gemini 2.5 Pro (best-in-class AI)
- 🎤 **Understand Voice** - Send voice notes while on scaffolding
- 📷 **Analyze Photos** - Upload site photos to verify against blueprints
- 🧠 **Remember Everything** - Recalls RFIs, change orders, and past decisions

**Premium AI Stack:** At $500/site, we use the absolute best models - Gemini 2.5 Pro with reasoning capabilities for maximum accuracy on critical construction data.

**Problem Solved:** Indian construction projects lose 6-15% of project value to rework. SiteMind prevents costly errors by giving engineers instant, accurate information.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- API Keys for:
  - Google Gemini (AI) - [aistudio.google.com](https://aistudio.google.com/apikey)
  - Twilio (WhatsApp) - [twilio.com](https://twilio.com)
  - Supabase (DB + Storage) - [supabase.com](https://supabase.com)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sitemind.git
cd sitemind/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from utils.database import init_db_sync; init_db_sync()"

# Run the server
python main.py
```

The API will be available at `http://localhost:8000`

### Test the Setup

```bash
# Run all integration tests
python prototype.py --test-all

# Interactive demo (requires Gemini API key)
python prototype.py --demo
```

## 📁 Project Structure

```
sitemind/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Configuration management
│   ├── prototype.py            # Testing & demo script
│   ├── requirements.txt        # Python dependencies
│   ├── routers/
│   │   ├── whatsapp.py         # WhatsApp webhook handlers
│   │   ├── admin.py            # Admin CRUD endpoints
│   │   └── analytics.py        # Usage analytics
│   ├── services/
│   │   ├── gemini_service.py   # Google Gemini AI
│   │   ├── whisper_service.py  # Voice transcription
│   │   ├── memory_service.py   # Long-term memory
│   │   ├── whatsapp_client.py  # Twilio WhatsApp
│   │   └── storage_service.py  # AWS S3 storage
│   ├── models/
│   │   ├── database.py         # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas
│   └── utils/
│       ├── database.py         # DB connection
│       ├── logger.py           # Logging config
│       └── helpers.py          # Utility functions
├── docs/                       # Documentation
├── tests/                      # Test files
└── admin-dashboard/            # Admin UI (future)
```

## 🔌 API Endpoints

### WhatsApp Webhook
- `POST /whatsapp/webhook` - Receive incoming messages
- `POST /whatsapp/status` - Message delivery status

### Admin API
- `POST /admin/builders` - Create builder/client
- `POST /admin/projects` - Create project/site
- `POST /admin/projects/{id}/blueprints` - Upload blueprints
- `POST /admin/projects/{id}/engineers` - Add site engineers
- `POST /admin/projects/{id}/memory` - Add project context

### Analytics
- `GET /analytics/dashboard` - Overall statistics
- `GET /analytics/projects/{id}` - Project analytics
- `GET /analytics/usage/daily` - Daily usage data

### Health
- `GET /health` - Service health check
- `GET /ping` - Simple uptime check

## ⚙️ Configuration

Required environment variables:

```env
# Google Gemini (AI)
GOOGLE_API_KEY=your-key

# OpenAI (Voice Transcription)
OPENAI_API_KEY=your-key

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/sitemind

# AWS S3 (File Storage)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET=sitemind-blueprints
```

## 🏛️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Site Engineer  │────▶│  WhatsApp API   │────▶│  SiteMind API   │
│   (WhatsApp)    │◀────│    (Twilio)     │◀────│   (FastAPI)     │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                        ┌────────────────────────────────┼────────────────────────────────┐
                        │                                │                                │
                        ▼                                ▼                                ▼
                ┌───────────────┐              ┌─────────────────┐              ┌─────────────────┐
                │  Gemini 2.0   │              │     Whisper     │              │   Supermemory   │
                │ (Blueprint AI)│              │(Voice to Text)  │              │ (Long-term Mem) │
                └───────────────┘              └─────────────────┘              └─────────────────┘
```

## 💰 Business Model

- **Price:** $500/site/month
- **Target:** 600 sites = $300,000/month
- **Market:** Large real estate developers in India

## 📈 Roadmap

- [x] Core API with Gemini integration
- [x] WhatsApp webhook handling
- [x] Voice note transcription
- [x] Blueprint upload and processing
- [ ] Admin dashboard UI
- [ ] Multi-language support
- [ ] Conflict detection
- [ ] Mobile app

## 🛠️ Development

```bash
# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/

# Format code
black backend/
isort backend/
```

## 📄 License

Proprietary - All rights reserved

## 🤝 Contact

Built with ❤️ for Indian construction industry

---

*"Preventing ₹10 Crore rework, one WhatsApp message at a time."*

