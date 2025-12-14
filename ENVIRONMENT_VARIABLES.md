# Environment Variables Documentation

## Required Variables

### `ADMIN_KEY` (REQUIRED)
- **Description:** Secret key for admin operations (creating license keys)
- **Type:** String
- **Example:** `openssl rand -hex 32`
- **Security:** Never commit this to version control
- **Default:** None (will raise error if not set)

## Optional Variables

### `DATABASE_PATH`
- **Description:** Path to SQLite database file
- **Type:** String
- **Default:** `almudeer.db`
- **Example:** `/var/lib/almudeer/almudeer.db`

### `FRONTEND_URL`
- **Description:** Frontend URL for CORS configuration
- **Type:** URL String
- **Default:** `https://almudeer.royaraqamia.com`
- **Example:** `https://app.example.com`

### `LOG_LEVEL`
- **Description:** Logging level
- **Type:** String
- **Options:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Default:** `INFO`
- **Example:** `DEBUG`

### `OLLAMA_BASE_URL`
- **Description:** Base URL for Ollama LLM service
- **Type:** URL String
- **Default:** `http://localhost:11434`
- **Example:** `http://ollama-server:11434`

### `OLLAMA_MODEL`
- **Description:** Ollama model name to use
- **Type:** String
- **Default:** `llama3.2`
- **Example:** `llama3.2` or `mistral`

### `REDIS_URL` (Optional)
- **Description:** Redis connection URL for caching
- **Type:** URL String
- **Default:** None (uses in-memory cache)
- **Example:** `redis://localhost:6379/0`
- **Note:** If not set, falls back to in-memory caching

## Example `.env` File

```bash
# Required
ADMIN_KEY=your-secure-random-key-here-change-this

# Database
DATABASE_PATH=almudeer.db

# Frontend
FRONTEND_URL=https://almudeer.royaraqamia.com

# Logging
LOG_LEVEL=INFO

# LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Optional: Redis Caching
# REDIS_URL=redis://localhost:6379/0
```

## Setting Environment Variables

### Linux/Mac
```bash
export ADMIN_KEY="your-key-here"
export LOG_LEVEL="DEBUG"
```

### Windows (PowerShell)
```powershell
$env:ADMIN_KEY="your-key-here"
$env:LOG_LEVEL="DEBUG"
```

### Using .env file
Create a `.env` file in the `backend/` directory:
```bash
ADMIN_KEY=your-key-here
LOG_LEVEL=INFO
```

The application will automatically load variables from `.env` using `python-dotenv`.

## Security Notes

1. **Never commit `.env` files** to version control
2. **Use strong, random keys** for `ADMIN_KEY`
3. **Rotate keys regularly** in production
4. **Use different keys** for development, staging, and production
5. **Restrict file permissions** on `.env` files: `chmod 600 .env`

## Generating Secure Keys

### Using OpenSSL
```bash
openssl rand -hex 32
```

### Using Python
```python
import secrets
secrets.token_urlsafe(32)
```

### Using Node.js
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

