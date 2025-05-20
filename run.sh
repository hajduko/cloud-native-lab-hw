#!/bin/bash
set -e  # Exit immediately if any command fails

echo "Starting the setup..."
sudo kubectl apply -f configmap.yaml

echo "Building Docker images..."
sudo docker build -t imagegrab:latest ./1_imagegrab
sudo docker build -t resize:latest ./2_resize
sudo docker build -t grayscale:latest ./3_grayscale
sudo docker build -t objectdetect:latest ./4_objectdetect
sudo docker build -t tag:latest ./5_tag

echo "Saving Docker images to tar files..."
sudo docker save -o imagegrab.tar imagegrab:latest
sudo docker save -o resize.tar resize:latest
sudo docker save -o grayscale.tar grayscale:latest
sudo docker save -o objectdetect.tar objectdetect:latest
sudo docker save -o tag.tar tag:latest

echo "Importing images into containerd (for k3s)..."
sudo ctr images import imagegrab.tar
sudo ctr images import resize.tar
sudo ctr images import grayscale.tar
sudo ctr images import objectdetect.tar
sudo ctr images import tag.tar

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