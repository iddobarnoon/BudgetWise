# Multi-stage build for BudgetWise Auth Service
FROM python:3.12-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared modules
COPY src/backend/shared ./src/backend/shared

# Copy service code
COPY src/backend/components/auth-service ./src/backend/components/auth-service

# Set Python path to include shared modules
ENV PYTHONPATH=/app/src/backend

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')"

# Run the service
CMD ["uvicorn", "src.backend.components.auth-service.app:app", "--host", "0.0.0.0", "--port", "8001"]
