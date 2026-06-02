FROM python:3.11-slim

# 1. ADDED MISSING SYSTEM DEPENDENCIES
# - pytesseract requires 'tesseract-ocr' installed on the OS level
# - openai-whisper requires 'ffmpeg' installed on the OS level to read audio
RUN apt-get update && apt-get install -y \
    libmagic1 \
    tesseract-ocr \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# (CPU-ONLY PYTORCH)
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

COPY apps/worker/requirements.txt .

# INSTALL REQUIREMENTS
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["celery", "-A", "apps.worker.main.celery_app", "worker", "--loglevel=info"]