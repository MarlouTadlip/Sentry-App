# Production Dockerfile for Sentry Backend
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies
# Extract dependencies from pyproject.toml and install with pip
RUN pip install --upgrade pip && \
    pip install django django-ninja django-cors-headers pydantic-settings pydantic \
    python-jose[cryptography] pillow psycopg2-binary firebase-admin google-genai httpx \
    gunicorn

# Copy project files
COPY sentry/ ./sentry/
COPY start-prod.sh ./

# Create directories for logs and media
RUN mkdir -p /app/sentry/logs /app/sentry/media

# Set permissions
RUN chmod +x /app/sentry/manage.py /app/start-prod.sh

# Expose port
EXPOSE 8000

# Use the production startup script
CMD ["/app/start-prod.sh"]

