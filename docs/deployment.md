# SiteMind Deployment Guide

## Quick Deployment Options

### Option 1: Railway.app (Recommended for MVP)

Railway provides zero-config deployment with built-in PostgreSQL.

1. **Connect Repository**
   ```bash
   # Push code to GitHub first
   railway login
   railway link
   ```

2. **Add PostgreSQL**
   - In Railway dashboard, add PostgreSQL plugin
   - Copy the `DATABASE_URL` to environment variables

3. **Configure Environment**
   Add these environment variables in Railway:
   ```
   GOOGLE_API_KEY=your-key
   OPENAI_API_KEY=your-key
   TWILIO_ACCOUNT_SID=your-sid
   TWILIO_AUTH_TOKEN=your-token
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   AWS_S3_BUCKET=sitemind-blueprints
   APP_ENV=production
   DEBUG=false
   ```

4. **Deploy**
   ```bash
   railway up
   ```

### Option 2: Docker Compose (Local/VPS)

```bash
# Clone the repository
git clone https://github.com/yourusername/sitemind.git
cd sitemind

# Create .env file
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f api
```

### Option 3: Manual Deployment

1. **Setup PostgreSQL**
   ```sql
   CREATE DATABASE sitemind;
   CREATE USER sitemind_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE sitemind TO sitemind_user;
   ```

2. **Setup Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt
   ```

3. **Configure Environment**
   ```bash
   export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/sitemind"
   export GOOGLE_API_KEY="your-key"
   # ... other variables
   ```

4. **Initialize Database**
   ```bash
   cd backend
   python -c "from utils.database import init_db_sync; init_db_sync()"
   ```

5. **Run with Gunicorn**
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
   ```

---

## Twilio WhatsApp Setup

### 1. Create Twilio Account
- Sign up at https://twilio.com
- Verify your phone number

### 2. Enable WhatsApp Sandbox (for testing)
- Go to Messaging > Try it out > Send a WhatsApp message
- Note the sandbox number (e.g., +14155238886)
- Join sandbox by sending code to the number

### 3. Configure Webhook
- In Twilio Console, go to WhatsApp Sandbox Settings
- Set webhook URL: `https://your-domain.com/whatsapp/webhook`
- Method: POST

### 4. Production WhatsApp (later)
- Apply for WhatsApp Business API
- Complete Meta Business verification
- Migrate from sandbox to production number

---

## AWS S3 Setup

### 1. Create S3 Bucket
```bash
aws s3 mb s3://sitemind-blueprints --region ap-south-1
```

### 2. Configure CORS
```json
{
  "CORSRules": [
    {
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST"],
      "AllowedOrigins": ["*"],
      "ExposeHeaders": []
    }
  ]
}
```

### 3. Create IAM User
Create a user with S3 access policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::sitemind-blueprints",
        "arn:aws:s3:::sitemind-blueprints/*"
      ]
    }
  ]
}
```

---

## Monitoring

### Sentry (Error Tracking)
1. Create account at https://sentry.io
2. Create new project (Python/FastAPI)
3. Add `SENTRY_DSN` to environment variables

### Health Checks
Configure your hosting provider to monitor:
- **Endpoint:** `GET /health`
- **Expected:** 200 status with `"status": "healthy"`
- **Interval:** Every 30 seconds

### Logging
Logs are written to:
- **Development:** Console (colorized)
- **Production:** `logs/sitemind_YYYY-MM-DD.log`

---

## Scaling Considerations

### Database
- Use connection pooling (already configured)
- Add read replicas for analytics queries
- Consider TimescaleDB for time-series metrics

### API
- Use Gunicorn with multiple workers
- Add Redis for caching common queries
- Implement rate limiting per user

### Storage
- Use S3 Transfer Acceleration for large uploads
- Set up CloudFront CDN for blueprint downloads

---

## Security Checklist

- [ ] Set strong `SECRET_KEY` for production
- [ ] Enable HTTPS (Railway does this automatically)
- [ ] Configure CORS for production domains only
- [ ] Use environment variables for all secrets
- [ ] Enable Twilio webhook signature validation
- [ ] Set up database backups
- [ ] Review S3 bucket permissions

