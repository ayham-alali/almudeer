# Database Migration Guide: SQLite → PostgreSQL

**Status:** Ready for migration  
**Estimated Time:** 30-60 minutes

---

## 📋 **PREREQUISITES**

1. **PostgreSQL installed and running**
   ```bash
   # Create database
   createdb almudeer
   ```

2. **Install asyncpg**
   ```bash
   pip install asyncpg
   ```

3. **Backup your SQLite database**
   ```bash
   cp almudeer.db almudeer.db.backup
   ```

---

## 🚀 **MIGRATION STEPS**

### Step 1: Set Environment Variables

```bash
# PostgreSQL connection string
export DATABASE_URL="postgresql://username:password@localhost:5432/almudeer"

# Optional: Keep SQLite path for migration script
export DATABASE_PATH="almudeer.db"
```

### Step 2: Run Migration Script

```bash
cd products/almudeer/backend
python migrate_to_postgresql.py
```

The script will:
- ✅ Export all data from SQLite
- ✅ Create PostgreSQL schema
- ✅ Import all data
- ✅ Verify migration

### Step 3: Update Application Configuration

```bash
# Set database type to PostgreSQL
export DB_TYPE=postgresql
export DATABASE_URL="postgresql://username:password@localhost:5432/almudeer"
```

### Step 4: Test Application

```bash
# Start the application
python main.py

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/auth/validate -X POST -H "Content-Type: application/json" -d '{"key":"YOUR_KEY"}'
```

### Step 5: Verify Data

```bash
# Connect to PostgreSQL
psql -d almudeer

# Check data
SELECT COUNT(*) FROM license_keys;
SELECT COUNT(*) FROM crm_entries;
SELECT COUNT(*) FROM usage_logs;
```

---

## ⚠️ **IMPORTANT NOTES**

1. **Keep SQLite Backup:** Don't delete `almudeer.db` until you've verified everything works
2. **Test Thoroughly:** Test all endpoints after migration
3. **Update All Services:** Make sure all services use new `DATABASE_URL`
4. **Connection Pooling:** PostgreSQL uses connection pooling automatically

---

## 🔄 **ROLLBACK PLAN**

If something goes wrong:

```bash
# 1. Stop application
# 2. Revert environment variables
export DB_TYPE=sqlite
export DATABASE_PATH=almudeer.db
unset DATABASE_URL

# 3. Restore from backup if needed
cp almudeer.db.backup almudeer.db

# 4. Restart application
```

---

## ✅ **VERIFICATION CHECKLIST**

After migration, verify:

- [ ] Health check endpoint works
- [ ] License validation works
- [ ] Can create new license keys
- [ ] Can save CRM entries
- [ ] Can retrieve CRM entries
- [ ] Usage logs are working
- [ ] All data migrated correctly
- [ ] Performance is acceptable

---

## 🎯 **NEXT STEPS**

After successful migration:

1. ✅ Update production environment variables
2. ✅ Set up automated backups for PostgreSQL
3. ✅ Configure connection pooling
4. ✅ Monitor performance
5. ✅ Remove SQLite dependencies (optional)

---

**Migration Complete!** 🎉

