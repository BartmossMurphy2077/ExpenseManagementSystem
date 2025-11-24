FROM python:3.11-slim

# Set working directory to /app (not /app/app)
WORKDIR /app

# Ensure pip is up-to-date
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && apt-get clean

# Copy backend source code
COPY ./app ./app

# Create data directory outside code
RUN mkdir -p /app/data

# Expose API port
EXPOSE 8000

# Set PYTHONPATH so 'app' package is discoverable
ENV PYTHONPATH=/app

# Start Uvicorn with proper module path
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
