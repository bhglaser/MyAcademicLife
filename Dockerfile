FROM python:3.12-slim

WORKDIR /app

# Install system deps for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY . .
RUN pip install --no-cache-dir ".[chatbot]"

# Ensure src/ is importable (pip installs as "profstack", not "src")
ENV PYTHONPATH=/app
ENV PORT=8080

# Run migrations then start the server
CMD alembic upgrade head && uvicorn src.app:app --host 0.0.0.0 --port $PORT
