# Railway Deployment Guide - Al-Mudeer Premium Backend

## 🚀 Complete Deployment Guide for Railway

This guide will help you deploy the Al-Mudeer backend to Railway with PostgreSQL database.

---

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI** (optional but recommended):
   ```bash
   npm i -g @railway/cli
   railway login
   ```

---

## Step 1: Create Railway Project

### Option A: Using Railway Dashboard

1. Go to [railway.app/dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo" (if you have a repo) or "Empty Project"

### Option B: Using Railway CLI

```bash
railway init
railway link
```

---

## Step 2: Add PostgreSQL Database

1. In your Railway project dashboard, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically create a PostgreSQL service
4. **Important**: Note the `DATABASE_URL` from the PostgreSQL service variables

---

## Step 3: Configure Environment Variables

In your Railway project, go to **Variables** tab and add:

### Required Variables

```env
# Database
DB_TYPE=postgresql
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Auto-set by Railway

# Security
ADMIN_KEY=your-super-secret-admin-key-here
ENCRYPTION_KEY=your-encryption-key-base64-here

# Application
LOG_LEVEL=INFO
PORT=${{PORT}}  # Auto-set by Railway

# Optional: LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Optional: Frontend URL (for CORS)
FRONTEND_URL=https://your-frontend-domain.com
```

### Generate Encryption Key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copy the output and set it as `ENCRYPTION_KEY`.

---

## Step 4: Deploy Backend

### Option A: Deploy from GitHub

1. Connect your GitHub repository to Railway
2. Railway will auto-detect the Python project
3. Set the **Root Directory** to `products/almudeer/backend` if needed
4. Railway will automatically:
   - Install dependencies from `requirements.txt`
   - Run migrations on startup
   - Start the application

### Option B: Deploy via CLI

```bash
cd products/almudeer/backend
railway up
```

### Option C: Deploy via Railway Dashboard

1. Click **"+ New"** → **"GitHub Repo"**
2. Select your repository
3. Set **Root Directory** to `products/almudeer/backend`
4. Railway will build and deploy automatically

---

## Step 5: Configure Build Settings

Railway will auto-detect Python, but you can customize:

### Build Command (if needed)
```bash
pip install -r requirements.txt
```

### Start Command
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
```

Or use the `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
```

---

## Step 6: Run Database Migrations

Migrations run automatically on startup, but you can also run manually:

### Using Railway CLI

```bash
railway run python run_migrations.py
```

### Or via Railway Dashboard

1. Go to your backend service
2. Click **"Deployments"** → **"New Deployment"**
3. Use command: `python run_migrations.py`

---

## Step 7: Verify Deployment

1. **Check Health Endpoint**:
   ```bash
   curl https://your-app-name.up.railway.app/health
   ```

2. **Check API Docs**:
   - Visit: `https://your-app-name.up.railway.app/docs`
   - Visit: `https://your-app-name.up.railway.app/redoc`

3. **Test Subscription Creation**:
   ```bash
   curl -X POST https://your-app-name.up.railway.app/api/admin/subscription/create \
     -H "Content-Type: application/json" \
     -H "X-Admin-Key: your-admin-key" \
     -d '{
       "company_name": "Test Company",
       "contact_email": "test@example.com",
       "days_valid": 365,
       "max_requests_per_day": 1000
     }'
   ```

---

## Step 8: Generate Domain (Optional)

Railway provides a default domain, but you can generate a custom one:

### Via Dashboard
1. Go to your service
2. Click **"Settings"** → **"Generate Domain"**
3. Choose a custom domain name

### Via CLI
```bash
railway domain
```

---

## Step 9: Monitor and Logs

### View Logs

**Via Dashboard**:
1. Go to your service
2. Click **"Deployments"** → Select a deployment → **"View Logs"**

**Via CLI**:
```bash
railway logs
```

### Monitor Health

The `/health` endpoint provides:
- Database connection status
- Cache availability
- Service version
- Timestamp

---

## Step 10: Production Checklist

- [ ] ✅ PostgreSQL database added and connected
- [ ] ✅ All environment variables set
- [ ] ✅ `ENCRYPTION_KEY` generated and set
- [ ] ✅ `ADMIN_KEY` set securely
- [ ] ✅ Database migrations completed
- [ ] ✅ Health check endpoint responding
- [ ] ✅ API documentation accessible
- [ ] ✅ Test subscription creation works
- [ ] ✅ Custom domain configured (if needed)
- [ ] ✅ Logs monitoring set up
- [ ] ✅ Background workers running (check logs)

---

## Troubleshooting

### Database Connection Issues

1. **Check `DATABASE_URL`**:
   ```bash
   railway variables
   ```
   Ensure `DATABASE_URL` is set correctly.

2. **Test Connection**:
   ```bash
   railway run python -c "import asyncpg; import asyncio; import os; asyncio.run(asyncpg.connect(os.getenv('DATABASE_URL')))"
   ```

### Application Won't Start

1. **Check Logs**:
   ```bash
   railway logs --tail
   ```

2. **Common Issues**:
   - Missing environment variables
   - Database not accessible
   - Port configuration (use `$PORT`)

### Background Workers Not Running

Check logs for:
```
Message polling workers started
```

If not present, check:
- Database connection
- Worker initialization errors in logs

---

## Scaling

### Horizontal Scaling

Railway automatically handles scaling, but you can configure:

1. **Workers**: Adjust `--workers` in start command
2. **Resources**: Upgrade plan for more CPU/memory

### Database Scaling

Railway PostgreSQL supports:
- Automatic backups
- Read replicas (Pro plan)
- Connection pooling (handled automatically)

---

## Security Best Practices

1. **Never commit secrets**: Use Railway variables
2. **Rotate keys regularly**: Update `ENCRYPTION_KEY` and `ADMIN_KEY` periodically
3. **Use HTTPS**: Railway provides SSL automatically
4. **Rate limiting**: Already implemented in the backend
5. **Input validation**: All endpoints sanitize input

---

## Backup and Recovery

### Database Backups

Railway PostgreSQL includes automatic backups:
- Daily backups retained for 7 days
- Manual backups available in dashboard

### Export Data

```bash
railway run pg_dump $DATABASE_URL > backup.sql
```

### Restore Data

```bash
railway run psql $DATABASE_URL < backup.sql
```

---

## Cost Optimization

1. **Use Railway Hobby Plan**: Free tier available
2. **Optimize Workers**: Start with 1-2 workers
3. **Database Size**: Monitor and clean old data
4. **Auto-sleep**: Railway can sleep inactive services (Hobby plan)

---

## Support

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- **Project Issues**: Check GitHub issues

---

## Next Steps

1. ✅ Deploy frontend (if separate)
2. ✅ Configure webhooks for WhatsApp/Telegram
3. ✅ Set up monitoring/alerting
4. ✅ Create first client subscription
5. ✅ Test end-to-end message flow

---

**🎉 Congratulations! Your Al-Mudeer backend is now deployed on Railway!**

