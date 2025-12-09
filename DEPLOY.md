# 🚀 SiteMind Deployment Guide

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   VERCEL        │     │   RAILWAY       │
│   Dashboard     │◀───▶│   Backend API   │
│   (Free)        │     │   ($5/month)    │
└─────────────────┘     └─────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   SUPABASE    │   │  SUPERMEMORY  │   │    TWILIO     │
│   Database    │   │    Memory     │   │   WhatsApp    │
│   ($25/mo)    │   │   ($19/mo)    │   │   (pay/use)   │
└───────────────┘   └───────────────┘   └───────────────┘
```

---

## Step 1: Deploy Backend to Railway

### 1.1 Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub

### 1.2 Deploy
```bash
# In sitemind/backend directory
cd /Users/arjun/sitemind/backend

# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Deploy
railway up
```

### 1.3 Add Environment Variables
In Railway dashboard → Variables, add:

```
GOOGLE_API_KEY=your_gemini_api_key
SUPERMEMORY_API_KEY=your_supermemory_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### 1.4 Get Your Backend URL
After deploy, Railway gives you a URL like:
`https://sitemind-backend-production.up.railway.app`

---

## Step 2: Deploy Dashboard to Vercel

### 2.1 Push to GitHub
```bash
cd /Users/arjun/sitemind

# Initialize git (if not done)
git init
git add .
git commit -m "SiteMind v1.0 - Ready for deployment"

# Push to GitHub
git remote add origin https://github.com/Arjun0606/sitemind-AI.git
git push -u origin main
```

### 2.2 Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click "New Project"
4. Import `sitemind-AI` repository
5. Set root directory to `dashboard`
6. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://your-railway-url.railway.app`
7. Deploy!

---

## Step 3: Configure Twilio Webhook

### 3.1 Get Your Railway URL
Your backend URL: `https://sitemind-xxx.railway.app`

### 3.2 Update Twilio
1. Go to [Twilio Console](https://console.twilio.com)
2. Messaging → Settings → WhatsApp Sandbox Settings
3. Set webhook URL to: `https://your-railway-url.railway.app/whatsapp/webhook`
4. Method: POST

---

## Step 4: Run Supabase Schema

1. Go to your Supabase project dashboard
2. SQL Editor
3. Paste and run the contents of `backend/database/schema.sql`
4. Create storage buckets:
   - `documents` (private)
   - `photos` (private)
   - `exports` (private)

---

## Step 5: Verify Deployment

### Test Backend
```bash
curl https://your-railway-url.railway.app/health
# Should return: {"status": "ok", "service": "sitemind"}
```

### Test WhatsApp
Send a message to your Twilio WhatsApp number.
You should get the premium welcome message.

### Test Dashboard
Visit your Vercel URL and you should see the dashboard.

---

## Monthly Costs

| Service | Cost |
|---------|------|
| Railway (Backend) | ~$5/month |
| Vercel (Dashboard) | FREE |
| Supabase Pro | $25/month |
| Supermemory Pro | $19/month |
| Twilio WhatsApp | ~$0.005/message |
| **TOTAL** | **~$50/month** |

Your subscription revenue: $1000/month
**Profit margin: 95%**

---

## Custom Domain (Optional)

### For Dashboard (Vercel)
1. Vercel Dashboard → Your Project → Settings → Domains
2. Add `dashboard.sitemind.ai` (or your domain)
3. Update DNS records

### For Backend (Railway)
1. Railway Dashboard → Your Project → Settings → Domains
2. Add `api.sitemind.ai`
3. Update DNS records

---

## Production Checklist

- [ ] Backend deployed to Railway
- [ ] Environment variables set in Railway
- [ ] Dashboard deployed to Vercel
- [ ] API URL set in Vercel env
- [ ] Twilio webhook configured
- [ ] Supabase schema executed
- [ ] Storage buckets created
- [ ] Test WhatsApp message works
- [ ] Test dashboard loads
- [ ] Custom domains (optional)

---

## Quick Commands

```bash
# Deploy backend
cd /Users/arjun/sitemind/backend
railway up

# Check logs
railway logs

# Redeploy after changes
git add .
git commit -m "Update"
git push
# Vercel auto-deploys from GitHub
# Railway: run `railway up` again
```

---

## Troubleshooting

### WhatsApp not responding
1. Check Railway logs: `railway logs`
2. Verify Twilio webhook URL is correct
3. Check environment variables are set

### Dashboard not loading
1. Check Vercel deployment logs
2. Verify `NEXT_PUBLIC_API_URL` is set correctly
3. Check CORS settings in backend

### AI not responding
1. Check `GOOGLE_API_KEY` is valid
2. Check Railway logs for errors
3. Verify Supermemory is connected

---

🎉 **You're live!** Go get that first customer!

