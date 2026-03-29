# Stage 1: Build environment
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production environment
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Create a non-root user
RUN adduser --disabled-password --gecos "" appuser && \
    mkdir -p /app/chroma_db && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy application files
COPY --chown=appuser:appuser . .

# Switch to the non-root user
USER appuser

EXPOSE 8088

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8088"]
