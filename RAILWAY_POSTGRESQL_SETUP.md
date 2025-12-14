# Railway PostgreSQL Setup Guide

**Using Railway for managed PostgreSQL - Easy! 🚀**

---

## 🚀 **STEP 1: Create PostgreSQL Database on Railway**

### Option A: Via Railway Dashboard

1. **Go to Railway Dashboard:**
   - Visit: https://railway.app
   - Login to your account

2. **Create New Project:**
   - Click "New Project"
   - Select "Empty Project" or use existing project

3. **Add PostgreSQL:**
   - Click "+ New" → "Database" → "Add PostgreSQL"
   - Railway will automatically provision PostgreSQL

4. **Get Connection String:**
   - Click on the PostgreSQL service
   - Go to "Variables" tab
   - Copy the `DATABASE_URL` (it's automatically created)

### Option B: Via Railway CLI

```bash
# Install Railway CLI (if not installed)
npm i -g @railway/cli

# Login
railway login

# Create new project (or use existing)
railway init

# Add PostgreSQL database
railway add --database postgres

# Get connection string
railway variables
# Look for DATABASE_URL
```

---

## 📋 **STEP 2: Set Up Environment Variables**

### Local Development:

```bash
# In your .env file or export:
export DB_TYPE=postgresql
export DATABASE_URL="postgresql://postgres:password@containers-us-west-xxx.railway.app:5432/railway"
```

### On Railway:

Railway automatically sets `DATABASE_URL` when you add PostgreSQL. You just need to set:

```bash
# In Railway dashboard → Variables:
DB_TYPE=postgresql
```

---

## 🔄 **STEP 3: Run Migration**

### Option A: Run Migration Locally

```bash
cd products/almudeer/backend

# Set Railway PostgreSQL URL
export DATABASE_URL="your_railway_postgres_url"

# Run migration
python migrate_to_postgresql.py
```

### Option B: Run Migration on Railway

1. **Add migration script to Railway:**
   - Create a one-time service or use Railway's "Run" feature
   - Or add it as a build step

2. **Or run via Railway CLI:**
   ```bash
   railway run python migrate_to_postgresql.py
   ```

---

## ✅ **STEP 4: Update Application**

### Update `database.py` to use Railway PostgreSQL:

The migration script will handle the data transfer. After migration:

1. **Set environment variables on Railway:**
   ```
   DB_TYPE=postgresql
   DATABASE_URL=<automatically set by Railway>
   ```

2. **Update your Railway service:**
   - Railway will automatically use `DATABASE_URL`
   - No code changes needed if using the unified database interface

---

## 🧪 **STEP 5: Test Connection**

### Test locally:

```bash
# Test PostgreSQL connection
python -c "
import asyncio
import asyncpg
import os

async def test():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    result = await conn.fetchval('SELECT version()')
    print(f'PostgreSQL version: {result}')
    await conn.close()

asyncio.run(test())
"
```

### Test on Railway:

```bash
# Deploy and check logs
railway logs

# Or test via Railway dashboard
# Go to your service → Logs
```

---

## 📊 **STEP 6: Verify Migration**

### Check data in Railway:

1. **Via Railway Dashboard:**
   - Go to PostgreSQL service
   - Click "Data" tab (if available)
   - Or use "Query" tab

2. **Via Railway CLI:**
   ```bash
   railway connect postgres
   # Then in psql:
   SELECT COUNT(*) FROM license_keys;
   SELECT COUNT(*) FROM crm_entries;
   ```

3. **Via Python:**
   ```python
   import asyncio
   import asyncpg
   import os
   
   async def verify():
       conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
       license_count = await conn.fetchval('SELECT COUNT(*) FROM license_keys')
       crm_count = await conn.fetchval('SELECT COUNT(*) FROM crm_entries')
       print(f'License keys: {license_count}')
       print(f'CRM entries: {crm_count}')
       await conn.close()
   
   asyncio.run(verify())
   ```

---

## 🔧 **RAILWAY-SPECIFIC CONFIGURATION**

### Update `railway.toml`:

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python main.py"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10

[env]
DB_TYPE = "postgresql"
# DATABASE_URL is automatically set by Railway
```

### Update `Procfile` (if using):

```
web: python main.py
```

---

## 🚨 **TROUBLESHOOTING**

### Connection Issues:

1. **Check Railway PostgreSQL is running:**
   - Dashboard → PostgreSQL service → Status should be "Active"

2. **Verify DATABASE_URL:**
   ```bash
   railway variables
   # Should show DATABASE_URL
   ```

3. **Test connection:**
   ```bash
   railway connect postgres
   # Should connect to psql
   ```

### Migration Issues:

1. **Backup first:**
   ```bash
   # Railway PostgreSQL has automatic backups
   # But you can also export:
   railway connect postgres
   pg_dump > backup.sql
   ```

2. **Check logs:**
   ```bash
   railway logs
   ```

---

## ✅ **CHECKLIST**

- [ ] PostgreSQL created on Railway
- [ ] DATABASE_URL copied/noted
- [ ] Environment variables set (DB_TYPE=postgresql)
- [ ] Migration script run successfully
- [ ] Data verified in PostgreSQL
- [ ] Application tested with PostgreSQL
- [ ] Railway service updated
- [ ] Health check passing
- [ ] All endpoints working

---

## 🎯 **NEXT STEPS AFTER MIGRATION**

1. ✅ Remove SQLite dependency (optional)
2. ✅ Set up automated backups (Railway does this automatically!)
3. ✅ Monitor database performance
4. ✅ Add connection pooling (already in code)
5. ✅ Set up alerts

---

## 💡 **RAILWAY ADVANTAGES**

✅ **Automatic Backups** - Railway handles backups automatically  
✅ **Easy Scaling** - Can scale PostgreSQL easily  
✅ **Monitoring** - Built-in metrics and logs  
✅ **SSL/TLS** - Automatic encryption  
✅ **No Maintenance** - Fully managed  

---

**Ready to migrate? Let's do it! 🚀**

