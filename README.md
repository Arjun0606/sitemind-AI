# 🏗️ SiteMind

**AI-powered construction site management via WhatsApp**

> Your construction site's AI brain - every blueprint, every decision, every query answered instantly.

---

## 💰 Pricing

```
$500/month flat + usage
```

**Included:**
- ✅ Unlimited users
- ✅ Unlimited projects
- ✅ 500 queries/month
- ✅ 20 documents/month
- ✅ 100 photos/month
- ✅ 10 GB storage

**Usage (when you exceed limits):**
- Query: $0.15
- Document: $2.50
- Photo: $0.50
- Storage: $1.00/GB

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/Arjun0606/sitemind-AI.git
cd sitemind-AI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 2. Configure

```bash
# Copy example env
cp .env.example .env

# Edit with your API keys
nano .env
```

### 3. Run

```bash
# Development
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Docker (optional)

```bash
docker-compose up -d
```

---

## ⚙️ Configuration

### Required API Keys

| Service | Purpose | Get it from |
|---------|---------|-------------|
| **Google Gemini** | AI reasoning | [makersuite.google.com](https://makersuite.google.com/app/apikey) |
| **Supermemory** | Long-term memory | [supermemory.ai/dashboard](https://supermemory.ai/dashboard) |
| **Supabase** | Database + Storage | [supabase.com](https://supabase.com) |
| **Twilio** | WhatsApp | [twilio.com](https://console.twilio.com) |

### Supabase Setup

1. Create project at [supabase.com](https://supabase.com)
2. Go to SQL Editor
3. Run `backend/database/schema.sql`
4. Create storage buckets: `documents`, `photos`, `exports`
5. Copy API keys to `.env`

### Twilio Setup

1. Create account at [twilio.com](https://twilio.com)
2. Go to Messaging > Try WhatsApp
3. Join sandbox (follow instructions)
4. Configure webhook URL: `https://your-domain.com/whatsapp/webhook`

---

## 📁 Project Structure

```
sitemind/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── database/
│   │   ├── schema.sql       # PostgreSQL schema
│   │   └── supabase_client.py
│   ├── services/
│   │   ├── gemini_service.py    # AI
│   │   ├── memory_service.py    # Long-term memory
│   │   ├── whatsapp_service.py  # Messaging
│   │   ├── storage_service.py   # Files
│   │   ├── pricing_service.py   # Pricing
│   │   └── billing_service.py   # Usage tracking
│   ├── routers/
│   │   ├── whatsapp.py      # Webhook
│   │   ├── admin.py         # Admin API
│   │   └── health.py        # Health checks
│   └── utils/
│       └── logger.py
├── Dockerfile
├── docker-compose.yml
├── railway.toml
└── README.md
```

---

## 🔌 API Endpoints

### Health
- `GET /` - App info
- `GET /health` - Service status

### WhatsApp
- `POST /whatsapp/webhook` - Twilio webhook

### Admin
- `POST /admin/companies` - Create company
- `POST /admin/users` - Create user
- `POST /admin/projects` - Create project
- `GET /admin/companies/{id}` - Get company
- `GET /admin/companies/{id}/users` - List users
- `GET /admin/billing/usage/{id}` - Get usage
- `GET /admin/billing/charges/{id}` - Get charges
- `POST /admin/billing/invoice/{id}` - Generate invoice
- `GET /admin/pricing` - Get pricing
- `GET /admin/pricing/calculate` - Calculate pricing

---

## 📱 WhatsApp Commands

| Command | Description |
|---------|-------------|
| `help` | Show help |
| `status` | Current usage |
| Send photo | AI analysis |
| Send PDF | Document storage |
| Ask question | AI answers |

---

## 🚀 Deployment

### Railway (Recommended)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up
```

### Docker

```bash
docker build -t sitemind .
docker run -p 8000:8000 --env-file backend/.env sitemind
```

---

## 📊 Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | FastAPI (Python) |
| **AI** | Google Gemini |
| **Memory** | Supermemory.ai |
| **Database** | Supabase (PostgreSQL) |
| **Storage** | Supabase Storage |
| **Messaging** | Twilio WhatsApp |
| **Deployment** | Railway / Docker |

---

## 📜 License

MIT

---

Built with ❤️ for Indian construction
