FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy application code
COPY . .
ENV PYTHONPATH=/app/backend

# Set working directory to backend
WORKDIR /app/backend

# Start command using shell form
CMD /bin/sh -c "alembic upgrade head && python scripts/create_admin.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"