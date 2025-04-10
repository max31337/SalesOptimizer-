FROM python:3.10-slim 

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Copy only the backend directory
COPY backend/ .

# Install Python dependencies with upgrade pip
RUN pip install --no-cache-dir --upgrade pip || (sleep 5 && pip install --no-cache-dir --upgrade pip)
RUN pip install --no-cache-dir -r requirements.txt || (sleep 5 && pip install --no-cache-dir -r requirements.txt)



# Set environment variables
ENV PYTHONPATH=/app

# Start the application
CMD sh -c "alembic upgrade head && python scripts/create_admin.py && uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"
