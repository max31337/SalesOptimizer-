FROM python:3.9-slim

WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY . .
ENV PYTHONPATH=/app/backend

CMD cd backend && alembic upgrade head && python scripts/create_admin.py && uvicorn app.main:app --host 0.0.0.0 --port $PORT