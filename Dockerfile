# /senior-health/Dockerfile (Corrected)

# Stage 1: Install Rust and build wheels
FROM rust:1.78 as builder

WORKDIR /usr/src/app

# Install Python 3.10 (venv package ko hata diya gaya hai)
RUN apt-get update && apt-get install -y python3.10 python3-pip

# Install maturin for building Rust-based Python packages
RUN pip install maturin

# Copy only the requirements files first to leverage Docker cache
COPY backend/requirements.txt ./backend/
COPY frontend/requirements.txt ./frontend/

# Install backend dependencies, building wheels from source
RUN pip install -r ./backend/requirements.txt


# Stage 2: Create the final, smaller image
FROM python:3.10-slim

WORKDIR /app

# Copy the built wheels from the builder stage
COPY --from=builder /root/.cache/pip /root/.cache/pip

# Copy the requirements files
COPY backend/requirements.txt ./backend/
COPY frontend/requirements.txt ./frontend/

# Install dependencies using the cached wheels
RUN pip install --no-index --find-links=/root/.cache/pip/wheels -r ./backend/requirements.txt
RUN pip install --no-index --find-links=/root/.cache/pip/wheels -r ./frontend/requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the ports
EXPOSE 8000
EXPOSE 8501

# We will define the start command on Render directly
