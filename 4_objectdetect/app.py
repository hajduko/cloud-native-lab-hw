import os
import cv2
import numpy as np
import redis
from minio import Minio
import json

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
BUCKET = os.getenv("BUCKET_NAME", "images")
GRAYSCALE = os.getenv("MINIO_GRAYSCALE", "grayscale")
DETECTED = os.getenv("MINIO_DETECTED", "detected")
TAGGED = os.getenv("MINIO_TAGGED", "tagged")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

net = cv2.dnn.readNetFromCaffe("./MobileNetSSD_deploy.prototxt",
                               "./MobileNetSSD_deploy.caffemodel")

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

def object_detect(image, origin_h, origin_w):
    print(f"Input image shape before cvtColor: {image.shape}")
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    (height, width) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(image, 0.007843, (height, width), 127.5)

    net.setInput(blob)
    detections = net.forward()

    labels_and_coords = []
    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.4:
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
        grayscale_image = cv2.imdecode(image_data, cv2.IMREAD_GRAYSCALE)

        labels_and_coords = object_detect(grayscale_image, int(h), int(w))

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