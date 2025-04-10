FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Copy only the backend directory
COPY backend/ .

# Install Python dependencies with upgrade pip
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Start the application
CMD sh -c "python scripts/wait_for_db.py && alembic upgrade head && python scripts/create_admin.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"