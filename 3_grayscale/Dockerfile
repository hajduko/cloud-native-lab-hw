FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir minio numpy opencv-python-headless redis

CMD ["python", "app.py"]