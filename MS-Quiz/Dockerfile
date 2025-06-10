FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8001

# Este CMD es el que debes usar, asumiendo 'app.py' y 'app = FastAPI()'
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]