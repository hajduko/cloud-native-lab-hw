import os
import cv2
import numpy as np
import redis
import time
from minio import Minio
from io import BytesIO

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
BUCKET = os.getenv("BUCKET_NAME")
GRAYSCALE = os.getenv("MINIO_GRAYSCALE")
DETECTED = os.getenv("MINIO_DETECTED")
TAGGED = os.getenv("MINIO_TAGGED")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

def object_detect(image, origin_h, origin_w):
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    (height, width) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(image, 0.007843, (height, width), 127.5)

    net.setInput(blob)
    detections = net.forward()

    labels_and_coords = []
    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > CONFIDENCE_MIN:
            idx = int(detections[0, 0, i, 1])
            # Mark area on the original-sized picture not the resized
            box = detections[0, 0, i, 3:7] * np.array([origin_w,
                                                       origin_h,
                                                       origin_w,
                                                       origin_h])
            (startX, startY, endX, endY) = box.astype("int")
            labels_and_coords.append(
                {"startX": int(startX),
                 "startY": int(startY),
                 "endX": int(endX),
                 "endY": int(endY),
                 "label": {"name": CLASSES[idx],
                           "index": int(idx)},
                 "confidence": float(confidence)})
    return labels_and_coords

def process(data):
    try:
        uid, h, w = data.split(";")
        grayscale_path = f"{uid}/{GRAYSCALE}.jpg"
        response = minio_client.get_object(BUCKET, grayscale_path)
        image_data = np.asarray(bytearray(response.read()), dtype="uint8")
        grayscale_image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        labels_and_coords = object_detect(grayscale_image, h, w)

        message = {
            "uid": uid,
            "labels_and_coords": labels_and_coords
        }

        redis_client.publish(TAGGED, json.dumps(message))
    except Exception as e:
        print("Error in detect:", e)

pubsub = redis_client.pubsub()
pubsub.subscribe(DETECTED)

print("Listening on detected...")

for msg in pubsub.listen():
    if msg["type"] == "message":
        process(msg["data"])