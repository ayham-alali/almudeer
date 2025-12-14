# Get Public PostgreSQL URL from Railway

The URL you have (`postgres.railway.internal`) is **internal-only** and only works from within Railway services.

For **local testing**, you need the **public URL**.

---

## 🔍 **How to Get Public URL:**

### Option 1: Railway Dashboard

1. Go to Railway Dashboard
2. Click on your **PostgreSQL service**
3. Go to **"Settings"** tab
4. Look for **"Public Networking"** section
5. Click **"Generate Public URL"** or **"Enable Public Networking"**
6. Copy the **public URL** (it will look like: `postgresql://postgres:xxx@containers-us-west-xxx.railway.app:5432/railway`)

### Option 2: Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Get public URL
railway variables
# Look for DATABASE_URL with public hostname
```

### Option 3: Use Railway's Connect Feature

1. In Railway Dashboard → PostgreSQL service
2. Click **"Connect"** button
3. It will show you connection strings including the public one

---

## ⚠️ **Important:**

- **Internal URL** (`postgres.railway.internal`) - Only works from Railway services
- **Public URL** (`containers-us-west-xxx.railway.app`) - Works from anywhere (your local machine, etc.)

For local migration, you need the **public URL**.

---

## 🚀 **Alternative: Run Migration on Railway**

If you can't get public URL, you can run the migration directly on Railway:

```bash
# Using Railway CLI
railway run python migrate_to_postgresql.py
```

This runs the script inside Railway's network where the internal URL works.

---

**Once you have the public URL, we can continue with the migration!**

