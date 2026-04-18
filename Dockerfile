# ── Enki AI — Multi-stage Dockerfile ─────────────────────────────────────────
#
# Stages:
#   backend   — Python FastAPI + Flask server (no GUI deps)
#   frontend  — Node/Vite dev server for the React companion UI
#
# Build the full stack with docker compose up --build

# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Python backend
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim AS backend

WORKDIR /app

# System deps needed for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install core Python deps (heavy optional deps excluded — install separately
# if you need mediapipe / opencv / build123d / pyaudio)
COPY requirements.txt .
RUN pip install --no-cache-dir \
    fastapi==0.115.12 \
    uvicorn==0.34.2 \
    python-socketio==5.12.1 \
    python-multipart==0.0.20 \
    python-dotenv==1.1.0 \
    python-docx==1.1.2 \
    PyPDF2==3.0.1 \
    flask==3.1.0 \
    flask-cors==5.0.1 \
    aiohttp==3.11.18 \
    pillow==11.2.1

# Copy application source
COPY enki_ai/ enki_ai/
COPY run.py .

# Create data directory for SQLite databases
RUN mkdir -p /app/data

EXPOSE 5000 7777

# Default: start the Flask REST API
CMD ["python", "-m", "enki_ai.api.web_server"]

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Node/Vite frontend
# ─────────────────────────────────────────────────────────────────────────────
FROM node:20-slim AS frontend

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

COPY src/ src/
COPY public/ public/
COPY index.html vite.config.js tailwind.config.js postcss.config.js ./

EXPOSE 5173

CMD ["npm", "run", "build"]
