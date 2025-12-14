# Quick Railway PostgreSQL Setup 🚀

**Fastest way to get PostgreSQL on Railway!**

---

## ⚡ **5-MINUTE SETUP**

### Step 1: Create PostgreSQL on Railway (2 min)

**Via Dashboard:**
1. Go to https://railway.app
2. Open your project (or create new)
3. Click "+ New" → "Database" → "Add PostgreSQL"
4. Wait for it to provision (~30 seconds)
5. Click on PostgreSQL service → "Variables" tab
6. **Copy the `DATABASE_URL`**

**Via CLI:**
```bash
railway add --database postgres
railway variables  # Get DATABASE_URL
```

### Step 2: Test Connection (1 min)

```bash
cd products/almudeer/backend

# Set DATABASE_URL
export DATABASE_URL="postgresql://postgres:xxx@containers-us-west-xxx.railway.app:5432/railway"

# Test connection
python setup_railway_postgres.py
```

### Step 3: Run Migration (2 min)

```bash
# Make sure DATABASE_URL is set
export DATABASE_URL="your_railway_postgres_url"

# Run migration
python migrate_to_postgresql.py
```

### Step 4: Update Railway Service

**In Railway Dashboard:**
1. Go to your backend service
2. Click "Variables" tab
3. Add: `DB_TYPE=postgresql`
4. `DATABASE_URL` is already set automatically
5. Redeploy service

**Or via CLI:**
```bash
railway variables set DB_TYPE=postgresql
railway up
```

---

## ✅ **VERIFY IT WORKS**

```bash
# Check health endpoint
curl https://your-app.railway.app/health

# Should show:
# {
#   "status": "healthy",
#   "database": "connected",
#   ...
# }
```

---

## 🎉 **DONE!**

Your backend is now using PostgreSQL on Railway!

**Benefits:**
- ✅ Automatic backups
- ✅ Scalable
- ✅ Managed (no maintenance)
- ✅ Production-ready

---

**Need help? Check `RAILWAY_POSTGRESQL_SETUP.md` for detailed guide.**

