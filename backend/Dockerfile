FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=600

# System deps utk Pillow / OpenCV / PaddleOCR
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
        libgomp1 curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-ocr.txt ./
RUN pip install --upgrade pip setuptools wheel \
 && pip install -r requirements.txt \
 && pip install -r requirements-ocr.txt

COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
