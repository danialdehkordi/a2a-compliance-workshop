FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn pydantic httpx aiosqlite python-multipart google-genai google-auth google-cloud-aiplatform cloudpickle

COPY pyproject.toml .
COPY app/ app/

EXPOSE 8080

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
