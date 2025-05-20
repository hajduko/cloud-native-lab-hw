FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask minio redis

CMD ["python", "app.py"]