FROM python:3.12-slim

WORKDIR /app

# Install system deps for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir ".[chatbot]"

COPY . .

# Railway sets PORT dynamically; default to 8000 for local use
ENV PORT=8000

# Run migrations then start the server
CMD alembic upgrade head && uvicorn src.app:app --host 0.0.0.0 --port $PORT
