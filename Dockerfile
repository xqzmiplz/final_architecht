FROM python:3.9-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8080
EXPOSE 9090
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--access-logfile", "-", "run:app"]