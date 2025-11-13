FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-tur \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV TESSERACT_PATH=/usr/bin/tesseract
ENV POPPLER_PATH=/usr/bin
ENV PORT=10000

EXPOSE 10000

CMD gunicorn --bind 0.0.0.0:$PORT --config gunicorn_config.py app:app
