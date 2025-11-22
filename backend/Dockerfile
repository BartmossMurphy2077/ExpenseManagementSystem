FROM python:3.12

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel

# Copy dependencies first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && apt-get clean

# Copy backend code
COPY ./app ./app

# Create data directory
RUN mkdir -p /app/data

# Expose API port
EXPOSE 8000

# Start Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
