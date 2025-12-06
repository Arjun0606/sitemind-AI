# 🏗️ SiteMind - The AI Site Engineer

> "Fleetline for Construction" - Give site engineers superpowers with AI

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

## 🎯 What is SiteMind?

SiteMind is an AI-powered assistant for construction site engineers in India. It combines:

- **📱 WhatsApp Interface** - Site engineers query via WhatsApp while on scaffolding
- **🖥️ Web Dashboard** - Management monitors ROI, analytics, and audit trails
- **🤖 Gemini 2.5 Pro** - Best-in-class AI for blueprint analysis

### Key Features

| Feature | Description |
|---------|-------------|
| 📐 **Blueprint Analysis** | AI reads and answers questions about construction drawings |
| 📷 **Photo Analysis** | Upload site photos to verify against blueprints |
| 🧠 **Project Memory** | Recalls RFIs, change orders, and all decisions |
| 📊 **ROI Tracking** | Shows estimated value delivered to justify subscription |
| 📋 **Audit Trail** | Complete history with citations for legal backing |
| 📈 **Auto Reports** | Weekly/monthly reports to stakeholders |

**Problem Solved:** Indian construction projects lose 6-15% of project value to rework. SiteMind prevents costly errors by giving engineers instant, accurate information.

## 💰 Pricing

| Sites | Discount | Price per Site |
|-------|----------|----------------|
| 1-2 sites | — | **$500/month** |
| 3-5 sites | 10% off | $450/month |
| 6-9 sites | 15% off | $425/month |
| 10+ sites | 25% off | $375/month |

**UNLIMITED queries** - No token limits, no usage caps. Everything included.

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SiteMind Platform                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Site Engineers                        Management               │
│   ┌─────────────┐                      ┌─────────────────┐       │
│   │  WhatsApp   │                      │  Web Dashboard  │       │
│   │  (Twilio)   │                      │  (Next.js)      │       │
│   └──────┬──────┘                      └────────┬────────┘       │
│          │                                      │                │
│          └──────────────────┬───────────────────┘                │
│                             │                                    │
│                    ┌────────▼────────┐                           │
│                    │  FastAPI Backend │                          │
│                    │  (Python 3.11+) │                           │
│                    └────────┬────────┘                           │
│                             │                                    │
│   ┌───────────────┬─────────┼─────────┬───────────────┐          │
│   │               │         │         │               │          │
│   ▼               ▼         ▼         ▼               ▼          │
│ ┌─────┐     ┌──────────┐ ┌──────┐ ┌────────┐   ┌──────────┐      │
│ │Gemini│     │Supermemory│ │Supabase│ │ ROI   │   │ Reports │     │
│ │2.5 Pro│    │(Memory)  │ │(DB/Files)│ │Service│   │ Service │    │
│ └─────┘     └──────────┘ └──────┘ └────────┘   └──────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
sitemind/
├── backend/                    # FastAPI Backend
│   ├── main.py                 # Entry point
│   ├── config.py               # Configuration
│   ├── prototype.py            # Testing & demo
│   ├── requirements.txt        # Dependencies
│   ├── routers/
│   │   ├── whatsapp.py         # WhatsApp webhooks
│   │   ├── admin.py            # Admin endpoints
│   │   └── analytics.py        # Analytics API
│   ├── services/
│   │   ├── gemini_service.py   # AI (Gemini 2.5 Pro)
│   │   ├── memory_service.py   # Project memory
│   │   ├── storage_service.py  # Supabase storage
│   │   ├── whatsapp_client.py  # Twilio client
│   │   ├── roi_service.py      # ROI calculations
│   │   ├── report_service.py   # Auto reports
│   │   ├── subscription_service.py  # Billing logic
│   │   └── pricing_service.py  # Pricing rules
│   ├── models/
│   │   ├── database.py         # SQLAlchemy models
│   │   └── schemas.py          # Pydantic schemas
│   └── utils/                  # Utilities
│
├── dashboard/                  # Next.js Dashboard
│   ├── src/
│   │   ├── pages/              # Dashboard pages
│   │   │   ├── index.tsx       # Overview
│   │   │   ├── sites/          # Site management
│   │   │   ├── analytics.tsx   # Analytics
│   │   │   ├── reports.tsx     # Reports
│   │   │   ├── users.tsx       # User management
│   │   │   ├── blueprints.tsx  # Blueprint management
│   │   │   ├── audit.tsx       # Audit trail
│   │   │   └── billing.tsx     # Billing
│   │   └── components/         # UI components
│   └── package.json
│
├── docs/                       # Documentation
├── tests/                      # Test files
├── Dockerfile                  # Container config
├── docker-compose.yml          # Local dev
└── railway.toml                # Railway deployment
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- API Keys:
  - [Google Gemini](https://aistudio.google.com/apikey)
  - [Twilio](https://twilio.com)
  - [Supabase](https://supabase.com)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your keys

# Run
python main.py
```

### Dashboard Setup

```bash
cd dashboard
npm install
npm run dev
```

### Test Everything

```bash
cd backend
python prototype.py --test-all
```

## ⚙️ Configuration

### Required Environment Variables

```env
# Google Gemini (AI)
GOOGLE_API_KEY=your-key

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Supabase (Database + Storage)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
DATABASE_URL=postgresql+asyncpg://...@...supabase.co:5432/postgres

# Optional: Supermemory.ai (Long-term memory)
SUPERMEMORY_API_KEY=your-key
```

## 🔌 API Endpoints

### WhatsApp
- `POST /whatsapp/webhook` - Receive messages
- `POST /whatsapp/status` - Delivery status

### Admin
- `POST /admin/builders` - Create builder
- `POST /admin/projects` - Create project/site
- `POST /admin/projects/{id}/blueprints` - Upload blueprints
- `POST /admin/projects/{id}/engineers` - Add engineers

### Analytics
- `GET /analytics/dashboard` - Overview stats
- `GET /analytics/projects/{id}` - Per-project data
- `GET /analytics/roi/{builder_id}` - ROI breakdown

### Health
- `GET /health` - Service status
- `GET /ping` - Uptime check

## 📈 Roadmap

- [x] Core API with Gemini 2.5 Pro
- [x] WhatsApp integration (Twilio)
- [x] Blueprint analysis
- [x] ROI tracking
- [x] Audit trail with citations
- [x] Auto-generated reports
- [x] Company hierarchy (builder → sites)
- [x] Volume pricing
- [x] Web dashboard (Next.js)
- [ ] Authentication (NextAuth)
- [ ] Real-time updates (WebSocket)
- [ ] Multi-language support
- [ ] Conflict detection
- [ ] Mobile app

## 🛠️ Development

```bash
# Backend with auto-reload
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Dashboard with HMR
cd dashboard
npm run dev

# Run tests
pytest tests/

# Format code
black backend/
```

## 📄 License

Proprietary - All rights reserved

## 🤝 Contact

Built with ❤️ for the Indian construction industry

---

*"Preventing ₹10 Crore rework, one WhatsApp message at a time."*
