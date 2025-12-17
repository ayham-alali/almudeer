#!/usr/bin/env python3
"""
Startup script for Railway deployment
Handles PORT environment variable properly
"""
import os
import subprocess
import sys

# Get port from environment, default to 8000
port = os.environ.get("PORT", "8000")

print(f"Starting server on port {port}...")

# Run uvicorn with the correct port
cmd = [
    sys.executable, "-m", "uvicorn",
    "main:app",
    "--host", "0.0.0.0",
    "--port", port
]

subprocess.run(cmd)
