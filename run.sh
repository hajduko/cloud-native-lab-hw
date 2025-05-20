#!/bin/bash
set -e  # Exit immediately if any command fails

echo "Starting the setup..."
sudo kubectl apply -f config.yaml

echo "Building Docker images..."
sudo docker build -t imagegrab:latest ./1_imagegrab
sudo docker save -o /tmp/imagegrab.tar imagegrab:latest
sudo ctr images import /tmp/imagegrab.tar
sudo rm /tmp/imagegrab.tar

sudo docker build -t resize:latest ./2_resize
sudo docker save -o /tmp/resize.tar resize:latest
sudo ctr images import /tmp/resize.tar
sudo rm /tmp/resize.tar

sudo docker build -t grayscale:latest ./3_grayscale
sudo docker save -o /tmp/grayscale.tar grayscale:latest
sudo ctr images import /tmp/grayscale.tar
sudo rm /tmp/grayscale.tar

sudo docker build -t objectdetect:latest ./4_objectdetect
sudo docker save -o /tmp/objectdetect.tar objectdetect:latest
sudo ctr images import /tmp/objectdetect.tar
sudo rm /tmp/objectdetect.tar

sudo docker build -t tag:latest ./5_tag
sudo docker save -o /tmp/tag.tar tag:latest
sudo ctr images import /tmp/tag.tar
sudo rm /tmp/tag.tar

echo "Deploying Redis and MinIO..."
sudo kubectl apply -f redis.yaml
sudo kubectl apply -f minio.yaml

echo "Deploying services..."
sudo kubectl apply -f 1_imagegrab/imagegrab_deployment.yaml
sudo kubectl apply -f 2_resize/resize_deployment.yaml
sudo kubectl apply -f 3_grayscale/grayscale_deployment.yaml
sudo kubectl apply -f 4_objectdetect/objectdetect_deployment.yaml
sudo kubectl apply -f 5_tag/tag_deployment.yaml

echo "All services deployed!"