# Stage 1: Build environment
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies required by some Python packages (e.g., chromadb)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install python dependencies to the user local directory
COPY requirements.txt .
RUN pip install --user --no-cache-dir --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Production environment
FROM python:3.11-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/appuser/.local/bin:$PATH

# Create a non-root user and setup directories
RUN adduser --disabled-password --gecos "" appuser && \
    mkdir -p /app/chroma_db && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application files
COPY --chown=appuser:appuser . .

EXPOSE 8088

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8088"]
