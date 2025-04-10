FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy application code
COPY . .

# Set environment and working directory
ENV PYTHONPATH=/app/backend
WORKDIR /app/backend

# Use shell form with absolute paths
CMD ["/bin/bash", "-c", "alembic upgrade head && python scripts/create_admin.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]