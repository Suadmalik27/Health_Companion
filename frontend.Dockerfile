# /senior-health/frontend.Dockerfile (Corrected Order)

# Stage 1: Build Stage
# HAR STAGE KI SHURUAAT HAMESHA 'FROM' SE HOTI HAI
FROM python:3.10-slim as builder

# Ab base box milne ke baad, zaroori tools install karein
RUN apt-get update && apt-get install -y git

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

CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
