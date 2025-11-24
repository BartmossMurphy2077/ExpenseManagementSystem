FROM python:3.11-slim

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && apt-get clean

COPY ./app ./app

# Create data directory for Azure persistence
RUN mkdir -p /home/data && chmod 777 /home/data

EXPOSE 8000

ENV PYTHONPATH=/app

# Initialize database BEFORE starting the server
CMD python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)" && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000
