FROM python:3.11-slim

# Install system deps for asyncpg + bcrypt
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cache deps separately from source code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Override in docker-compose to enable --reload during dev
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
