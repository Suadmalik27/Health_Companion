# /senior-health/Dockerfile (Final, More Robust Version)

# Stage 1: Build Stage with Rust
FROM rust:1.78 as builder

# Install Python 3.10
RUN apt-get update && apt-get install -y python3.10 python3-pip

# Set up a virtual environment
RUN python3.10 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install them, building wheels
COPY backend/requirements.txt /app/backend/
COPY frontend/requirements.txt /app/frontend/
RUN pip install --upgrade pip
RUN pip wheel --no-cache-dir --wheel-dir=/app/wheels -r /app/backend/requirements.txt
RUN pip wheel --no-cache-dir --wheel-dir=/app/wheels -r /app/frontend/requirements.txt


# Stage 2: Final Production Stage
FROM python:3.10-slim

# Create a non-root user
RUN useradd --create-home appuser
USER appuser
WORKDIR /home/appuser/app

# Set up a virtual environment
RUN python3.10 -m venv /home/appuser/venv
ENV PATH="/home/appuser/venv/bin:$PATH"

# Copy built wheels and install them
COPY --from=builder /app/wheels /app/wheels
RUN pip install --no-cache-dir --no-index --find-links=/app/wheels /app/wheels/*

# Copy application code
COPY --chown=appuser:appuser . .

# Expose ports
EXPOSE 8000
EXPOSE 8501
