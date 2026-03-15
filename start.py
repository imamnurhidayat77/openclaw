"""Entrypoint for Railway deployment. Reads PORT from environment."""

import os
import sys

import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", os.environ.get("APP_PORT", "8000")))
    print(f"[start] Python {sys.version}", flush=True)
    print(f"[start] PORT env = {os.environ.get('PORT', 'NOT SET')}", flush=True)
    print(f"[start] Binding to 0.0.0.0:{port}", flush=True)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
