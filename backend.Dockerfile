# /senior-health/backend.Dockerfile

# Stage 1: Build Stage
FROM python:3.10-slim as builder
WORKDIR /app
COPY backend/requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/app/wheels -r requirements.txt

# Stage 2: Final Production Stage
FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /app/wheels /app/wheels
RUN pip install --no-cache-dir --no-index --find-links=/app/wheels /app/wheels/*
COPY backend/ .
EXPOSE 8000

# YEH HAI NAYI AUR ZAROORI LINE
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
