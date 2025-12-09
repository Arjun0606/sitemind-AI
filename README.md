# 🧠 SiteMind - Your Project Brain

> **Connected Intelligence for Construction**
> 
> Cross-reference everything. Catch every expensive mistake.

---

## What is SiteMind?

SiteMind is an AI-powered construction assistant that:

- **Stores everything** - Every drawing, decision, photo, and conversation
- **Connects everything** - AI cross-references photos against specs
- **Catches everything** - Mismatches detected before they become expensive

**Result:** ₹10-30 lakh saved per month by catching rework before it happens.

---

## How It Works

```
1. UPLOAD SPECS
   Site engineer sends drawing PDF via WhatsApp
   AI extracts: "Column B2: 450mm, 12mm rebar @ 150mm"
   
2. SEND SITE PHOTO  
   Engineer takes photo of Column B2 rebar
   AI sees: "10mm rebar @ 200mm spacing"
   
3. MISMATCH CAUGHT!
   ⚠️ "Photo shows 10mm @ 200mm"
   📐 "Spec says 12mm @ 150mm"
   💰 "Fix now or ₹4-5 lakh rework"

4. VALUE DELIVERED
   Problem caught before concrete pour
   ₹5 lakh saved
```

---

## Tech Stack

| Service | Purpose | Cost |
|---------|---------|------|
| **Gemini 3 Pro** | AI brain | ~$0.008/query |
| **Supermemory.ai** | Project memory | $19/month |
| **Supabase** | Database + Storage | $25/month |
| **Twilio** | WhatsApp API | ~$0.005/msg |

---

## Pricing

```
$1,000 USD/month per company

INCLUDED:
✓ Unlimited projects
✓ Unlimited users  
✓ 1,000 AI queries
✓ 50 documents
✓ 200 photos
✓ 50 GB storage

OVERAGES:
• Query: $0.25
• Document: $0.45
• Photo: $0.15
• Storage: $2/GB
```

---

## Quick Start

### 1. Setup Environment

```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Database

Run `database/schema.sql` in your Supabase SQL editor.

### 4. Run Server

```bash
uvicorn main:app --reload
```

### 5. Configure Twilio Webhook

Point your Twilio WhatsApp webhook to:
```
https://your-domain.com/whatsapp/webhook
```

---

## Project Structure

```
sitemind/
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── config.py                  # Settings
│   ├── routers/
│   │   ├── whatsapp.py           # WhatsApp webhook
│   │   ├── dashboard.py          # Dashboard API
│   │   └── admin.py              # Admin endpoints
│   ├── services/
│   │   ├── gemini_service.py     # AI (Gemini)
│   │   ├── memory_service.py     # Memory (Supermemory)
│   │   ├── connected_intelligence.py  # THE CORE
│   │   ├── sitemind_core.py      # Main AI processing
│   │   ├── whatsapp_service.py   # Twilio
│   │   ├── storage_service.py    # Supabase storage
│   │   ├── billing_service.py    # Usage tracking
│   │   └── pricing_service.py    # Pricing rules
│   └── database/
│       └── schema.sql            # PostgreSQL schema
│
├── dashboard/                     # Next.js web dashboard
│   └── src/pages/
│       ├── index.tsx             # Main dashboard
│       ├── alerts.tsx            # Mismatch alerts
│       └── ...
│
└── BUSINESS_PLAN.md              # Full business plan
```

---

## API Endpoints

### WhatsApp
- `POST /whatsapp/webhook` - Receive messages from Twilio

### Dashboard API
- `GET /api/dashboard/stats/{company_id}` - Company stats
- `GET /api/dashboard/alerts/{company_id}` - Mismatch alerts
- `GET /api/dashboard/reports/leakage/{company_id}` - Value report
- `GET /api/dashboard/billing/usage/{company_id}` - Usage & billing
- `GET /api/dashboard/specs/{company_id}` - Stored specifications
- `GET /api/dashboard/search/{company_id}?q=query` - Search memory

---

## WhatsApp Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/project` | List/switch projects |
| `/specs` | View stored specifications |
| `/alerts` | View mismatch alerts |
| `/report` | Get value protected report |
| `/search [query]` | Search project memory |
| `/value` | Show value protected |

---

## The Core Value

```
WITHOUT SITEMIND:
─────────────────
• Info scattered across 10+ WhatsApp groups
• Wrong specs used → Rework → ₹5 lakh loss
• "What did architect say?" → Nobody knows
• Disputes → No proof

WITH SITEMIND:
──────────────
• Single Project Brain
• Photo cross-ref → Caught in real-time
• Every question answered with citation
• Full audit trail with sources
```

---

## License

Proprietary - All rights reserved

---

**SiteMind: Zero information gaps. Zero money leaks.**
