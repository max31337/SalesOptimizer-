FROM python:3.9-slim

WORKDIR /backend

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Copy only the backend directory
COPY backend/ .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

# Start the application: wait for DB, run migrations, then start server
CMD ["sh", "-c", "\
    echo 'Waiting for database...' && \
    python scripts/wait_for_db.py && \
    echo 'Running Alembic migrations...' && \
    alembic upgrade head && \
    echo 'Creating admin user...' && \
    python scripts/create_admin.py && \
    echo 'Starting FastAPI server...' && \
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]