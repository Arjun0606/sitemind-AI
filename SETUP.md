# SiteMind Setup Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Get API Keys

| Service | URL | Plan | Cost |
|---------|-----|------|------|
| **Supermemory** | [console.supermemory.ai](https://console.supermemory.ai) | Pro | $19/mo |
| **Supabase** | [supabase.com/dashboard](https://supabase.com/dashboard) | Pro | $25/mo |
| **Google AI** | [aistudio.google.com](https://aistudio.google.com/app/apikey) | Pay-as-you-go | ~$0.008/query |
| **Twilio** | [console.twilio.com](https://console.twilio.com) | Pay-as-you-go | $15/mo base |

**Total fixed cost: ~$79/month**

---

### Step 2: Supermemory Setup

1. Go to [console.supermemory.ai](https://console.supermemory.ai)
2. Sign up / Log in
3. Go to **Billing** → **Upgrade to Pro** ($19/month)
4. Go to **API Keys** → **Create New Key**
5. Copy the API key

---

### Step 3: Supabase Setup

1. Go to [supabase.com/dashboard](https://supabase.com/dashboard)
2. Click **New Project**
3. Name: `sitemind-prod`
4. Generate a strong database password (save it!)
5. Region: Choose closest to your users
6. Click **Create Project** (wait 2 min)

**Get your keys:**
- Go to **Settings** → **API**
- Copy: `Project URL`, `anon public`, `service_role`

**Create database tables:**
- Go to **SQL Editor**
- Paste the contents of `backend/database/schema.sql`
- Click **Run**

**Create storage buckets:**
- Go to **Storage**
- Create buckets: `documents`, `photos`, `exports`

---

### Step 4: Google AI (Gemini) Setup

1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Sign in with Google
3. Click **Get API Key** → **Create API key**
4. Copy the API key

---

### Step 5: Twilio Setup (WhatsApp)

1. Go to [console.twilio.com](https://console.twilio.com)
2. Sign up / Log in
3. Get your **Account SID** and **Auth Token** from dashboard
4. Go to **Messaging** → **Try it out** → **Send a WhatsApp message**
5. Follow the sandbox setup instructions
6. Your sandbox number: `whatsapp:+14155238886`

**For production:** Apply for WhatsApp Business API approval

---

### Step 6: Configure Environment

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your keys:

```env
# Supermemory
SUPERMEMORY_API_KEY=sm_xxxxxxxxxxxx

# Google Gemini
GOOGLE_API_KEY=AIzaxxxxxxxxxxxxxxxx

# Supabase
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

---

### Step 7: Test Setup

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Test Supermemory
python test_supermemory.py

# Start the server
python main.py
```

You should see:
```
✅ Supermemory connected
✅ Supabase connected
✅ Gemini configured
🚀 Server running on http://localhost:8000
```

---

### Step 8: Test WhatsApp

1. Send "join <sandbox-code>" to your Twilio WhatsApp number
2. Send "hi" to test
3. You should get a response from SiteMind!

---

## 📊 Verify Margins

Run the pricing calculator:

```bash
python -c "from services.pricing_service import pricing_service; print(pricing_service.print_margin_report())"
```

Expected output:
```
Query:    91% margin ✅
Document: 90% margin ✅
Photo:    90% margin ✅
Storage:  94% margin ✅
```

---

## 🎯 You're Ready!

- **Test locally**: `python main.py`
- **Deploy to Railway**: Connect GitHub repo
- **First customer**: Start pilot program!

---

## 💰 Monthly Costs at Scale

| Customers | Revenue | Costs | Profit |
|-----------|---------|-------|--------|
| 1 | $5,628 | $543 | $5,085 |
| 10 | $56,280 | $5,430 | $50,850 |
| 50 | $281,375 | $27,150 | $254,225 |
| 71 | $399,552 | $38,553 | $360,999 |

**71 customers = $400k/month revenue, 90% profit margin** 🎉

