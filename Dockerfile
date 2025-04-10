FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY backend/ backend/
ENV PYTHONPATH=/app/backend
WORKDIR /app/backend

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

# Use shell form with absolute paths
CMD alembic upgrade head && \
    python scripts/create_admin.py && \
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT}