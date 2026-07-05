FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for psycopg
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# NOTE: Copy everything before pip install to ensure cache is invalidated
# when requirements.txt or any code file changes.
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Use $PORT for Railway dynamic port assignment
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
