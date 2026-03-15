# ============================================================
# Stage 1: Base image
# ============================================================
FROM python:3.12-slim AS base

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ============================================================
# Stage 2: Dependencies
# ============================================================
FROM base AS deps

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================
# Stage 3: Production
# ============================================================
FROM deps AS production

# Copy application code
COPY app/ ./app/
COPY static/ ./static/
COPY start.py ./

# Create non-root user for security
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://localhost:' + os.environ.get('PORT','8000') + '/health')" || exit 1

# Run with uvicorn — Railway injects PORT env var
CMD ["python", "start.py"]
