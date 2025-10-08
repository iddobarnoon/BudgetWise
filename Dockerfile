# BudgetWise Backend Services Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY src/backend /app

# Set Python path for clean imports
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose ports for all services
EXPOSE 8001 8002 8003 8004

# Default command (will be overridden by docker-compose)
CMD ["uvicorn", "components.pipeline.main:app", "--host", "0.0.0.0", "--port", "8004"]
