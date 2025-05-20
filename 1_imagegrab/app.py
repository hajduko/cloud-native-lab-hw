import os
import uuid
from flask import Flask, request, jsonify
from minio import Minio
from redis import Redis

app = Flask(__name__)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
BUCKET = os.getenv("MINIO_BUCKET")
ORIGINAL = os.getenv("MINIO_ORIGINAL")
RESIZED = os.getenv("MINIO_RESIZED")

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    if not file:
        return jsonify({'error': 'No image uploaded'}), 400

    uid = str(uuid.uuid4())
    original_path = f"{uid}/{ORIGINAL}.jpg"

    minio_client.put_object(BUCKET, original_path, file.stream, length=-1, part_size=10*1024*1024)

    redis_client.publish(RESIZED, uid)
    return jsonify({"message": "Image uploaded", "id": uid})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
