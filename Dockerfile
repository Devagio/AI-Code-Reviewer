
# 1. A lightweight, maintained Python base image (argument for flexibility)
ARG PYTHON_VERSION=3.12-slim-bullseye
FROM python:${PYTHON_VERSION}

# 2. System Environment and Dependency Setup
# Set environment variables for Python (better Docker behavior)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system-level dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    libjpeg-dev \
    libcairo2 \
    # Add any other needed OS packages here
    && rm -rf /var/lib/apt/lists/*

# 3. Virtual Environment (Optional but recommended for Python isolation)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 4. Set up working directory and copy requirements first for better Docker caching
WORKDIR /app

# Copy requirements before code for Docker cache optimization
COPY requirements.txt /tmp/requirements.txt

# Upgrade pip and install dependencies in the venv
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# 5. Copy the application code
COPY . /app

# ------------------------------------------------------------------------------
# 6. Add a non-root user (optional for security)
# ------------------------------------------------------------------------------
# RUN adduser --disabled-password appuser
# USER appuser

# ------------------------------------------------------------------------------
# 7. Environment variables for app secrets/configuration (never hardcoded)
# ------------------------------------------------------------------------------
# (All secrets/configs should come from environment variables or a secret manager)
# Example:
# ENV OPENAI_API_KEY=<set-in-docker-compose-or-k8s>
# ENV GITHUB_TOKEN=<set-in-docker-compose-or-k8s>

# ------------------------------------------------------------------------------
# 8. Expose the FastAPI app port
# ------------------------------------------------------------------------------
EXPOSE 8000

# ------------------------------------------------------------------------------
# 9. Entrypoint scripts for different services (app & Celery)
# ------------------------------------------------------------------------------
# Use entrypoint scripts or pass commands via docker-compose

# Default command to run FastAPI app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ------------------------------------------------------------------------------
# 10. To run the Celery worker, override the command in docker-compose:
#    command: celery -A app.api.tasks worker --loglevel=info
# ------------------------------------------------------------------------------

