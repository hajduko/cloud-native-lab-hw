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
ORIGINAL = os.getenv("MINIO_ORIGINAL")
TAGGED = os.getenv("MINIO_TAGGED")

redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
minio_client = Minio(MINIO_ENDPOINT, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

def tag_image(labels_and_coords, origin_image):
    image = copy.deepcopy(origin_image)
    for label_and_coord in labels_and_coords:
        label = label_and_coord["label"]["name"]
        index = label_and_coord["label"]["index"]
        startY = label_and_coord["startY"]
        cv2.rectangle(image,
                      (label_and_coord["startX"],
                       startY),
                      (label_and_coord["endX"],
                       label_and_coord["endY"]),
	    	              COLORS[index], 2)
        y = startY
        cv2.putText(image, label, (label_and_coord["startX"], y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    COLORS[index], 2)
    return image

def process(data):
    try:
        decoded_data = json.loads(data)
        uid = decoded_data["uid"]
        labels_and_coords = decoded_data["labels_and_coords"]

        original_path = f"{uid}/{ORIGINAL}.jpg"
        response = minio_client.get_object(BUCKET, original_path)
        image_data = np.asarray(bytearray(response.read()), dtype="uint8")
        original_image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        tagged_image = tag_image(original_image, labels_and_coords)

        tagged_path = f"{uid}/result.jpg"
        tagged_bytes = cv2.imencode('.jpg', tagged_image)[1].tobytes()

        minio_client.put_object(BUCKET, tagged_path, BytesIO(tagged_bytes), len(tagged_bytes))
    except Exception as e:
        print("Error in tag:", e)

pubsub = redis_client.pubsub()
pubsub.subscribe(TAGGED)

print("Listening on tagged...")

for msg in pubsub.listen():
    if msg["type"] == "message":
        process(msg["data"])