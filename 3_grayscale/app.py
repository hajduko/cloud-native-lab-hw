import os
import cv2
import numpy as np
import redis
from minio import Minio
from io import BytesIO

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
BUCKET = os.getenv("BUCKET_NAME")
RESIZED = os.getenv("MINIO_RESIZED")
GRAYSCALE = os.getenv("MINIO_GRAYSCALE")
DETECTED = os.getenv("MINIO_DETECTED")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

def grayscale_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def process(data):
    try:
        uid, h, w = data.split(";")
        resized_path = f"{uid}/{RESIZED}.jpg"
        response = minio_client.get_object(BUCKET, resized_path)
        image_data = np.asarray(bytearray(response.read()), dtype="uint8")
        resized_image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        grayscale_image = grayscale_image(resized_image)

        grayscale_path = f"{uid}/{GRAYSCALE}.jpg"
        grayscale_bytes = cv2.imencode('.jpg', grayscale_image)[1].tobytes()

        minio_client.put_object(BUCKET, grayscale_path, BytesIO(grayscale_bytes), len(grayscale_bytes))
        redis_client.publish(DETECTED, f"{uid};{h};{w}")
    except Exception as e:
        print("Error in grayscale:", e)

pubsub = redis_client.pubsub()
pubsub.subscribe(GRAYSCALE)

print("Listening on grayscale...")

for msg in pubsub.listen():
    if msg["type"] == "message":
        process(msg["data"].decode("utf-8"))