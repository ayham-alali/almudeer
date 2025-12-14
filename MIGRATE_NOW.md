# Ready to Migrate? Follow These Steps

---

## ✅ **STEP 1: Verify Database is Connected**

In Railway Dashboard:
- Go to **Postgres** service → **Database** tab
- Make sure it shows **"Connected"** (not "Attempting...")
- If still connecting, wait 1-2 more minutes

---

## ✅ **STEP 2: Get DATABASE_URL**

In Railway Dashboard:
1. Go to **Postgres** service → **Variables** tab
2. Find **`DATABASE_URL`**
3. **Copy the value** (it's the internal Railway URL)

It should look like:
```
postgresql://postgres:xxx@postgres.railway.internal:5432/railway
```

---

## ✅ **STEP 3: Run Migration**

You have **2 options**:

### **Option A: Using Railway CLI** (Recommended - Uses Internal Network)

```bash
# Make sure you're in the backend directory
cd products/almudeer/backend

# Set the DATABASE_URL (use the internal one from Railway)
export DATABASE_URL="postgresql://postgres:YmXFyjeYZdrUSpixHuqyRkEWeBHCaaqb@postgres.railway.internal:5432/railway"

# Run migration using Railway CLI (runs inside Railway's network)
railway run python migrate_to_postgresql.py
```

### **Option B: Using Railway Database Interface** (If CLI doesn't work)

1. In Railway Dashboard → **Postgres** → **Database** tab
2. Once connected, you'll see a SQL query interface
3. We can run the schema creation SQL there
4. Then import data separately

---

## ✅ **STEP 4: After Migration**

1. **Update Railway Backend Service:**
   - Go to your **almudeer** backend service
   - **Variables** tab
   - Add: `DB_TYPE=postgresql`
   - `DATABASE_URL` is automatically set by Railway

2. **Redeploy:**
   - Click **"Redeploy"** or push new code
   - Check logs to verify it's using PostgreSQL

---

## 🚀 **READY?**

**First, confirm:**
- [ ] Database shows "Connected" in Railway
- [ ] You have the `DATABASE_URL` from Variables tab

**Then run:**
```bash
railway run python migrate_to_postgresql.py
```

**Or if Railway CLI isn't set up, let me know and we'll use the database interface!**

