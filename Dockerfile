FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8501

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-eng && \
    rm -rf /var/lib/apt/lists/* && \
    python -m pip install --upgrade pip && \
    python -m pip install -r /app/requirements.txt

COPY . /app

RUN python -m pip install . && \
    chmod +x /app/start.sh && mkdir -p /app/data/uploads

EXPOSE 8501

CMD ["bash", "/app/start.sh"]
