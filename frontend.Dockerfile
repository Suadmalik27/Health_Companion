# /senior-health/frontend.Dockerfile

# Stage 1: Build Stage
FROM python:3.10-slim as builder
WORKDIR /app
COPY frontend/requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/app/wheels -r requirements.txt

# Stage 2: Final Production Stage
FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /app/wheels /app/wheels
RUN pip install --no-cache-dir --no-index --find-links=/app/wheels /app/wheels/*
COPY frontend/ .
EXPOSE 8501

# YEH HAI NAYI AUR ZAROORI LINE
CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
