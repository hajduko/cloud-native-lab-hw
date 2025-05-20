import os
import cv2
import numpy as np
import redis
from minio import Minio
from io import BytesIO

print("Starting resize service...")

SCALE_PERCENT = int(os.getenv("SCALE_PERCENT", 25))
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
BUCKET = os.getenv("BUCKET_NAME", "images")
ORIGINAL = os.getenv("MINIO_ORIGINAL", "original")
RESIZED = os.getenv("MINIO_RESIZED", "resized")
GRAYSCALE = os.getenv("MINIO_GRAYSCALE", "grayscale")

print("Environment variables are read successfully.")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

print("Connecting to MinIO and Redis...")

def resize_image(image):
    origin_h, origin_w = image.shape[:2]
    width = int(origin_w * SCALE_PERCENT / 100)
    height = int(origin_h * SCALE_PERCENT / 100)
    image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
    return image, origin_h, origin_w

def process(uid):
    try:
        original_path = f"{uid}/{ORIGINAL}.jpg"
        print(f"Fetching object: bucket={BUCKET}, path={original_path}", flush=True)

        response = minio_client.get_object(BUCKET, original_path)
        with response as stream:
            image_bytes = stream.read()
            print(f"Fetched {len(image_bytes)} bytes", flush=True)
            image_data = np.asarray(bytearray(image_bytes), dtype="uint8")
            origin_image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        resized_image, h, w = resize_image(origin_image)

        resized_path = f"{uid}/{RESIZED}.jpg"
        resized_bytes = cv2.imencode('.jpg', resized_image)[1].tobytes()

        minio_client.put_object(BUCKET, resized_path, BytesIO(resized_bytes), len(resized_bytes))
        redis_client.publish(GRAYSCALE, f"{uid};{h};{w}")
    except Exception as e:
        print("Error in resize:", e)

pubsub = redis_client.pubsub()
pubsub.subscribe(RESIZED)

print("Listening on resize...")

for msg in pubsub.listen():
    if msg["type"] == "message":
        print("Received message:", msg, flush=True)
        uid = msg.get("data")
        if isinstance(uid, str) and uid.strip():
            process(uid)
        else:
            print("Invalid UID received:", uid, flush=True)