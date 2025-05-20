#!/bin/bash
set -e  # Exit immediately if any command fails

echo "Installing config..."
echo ""

sudo kubectl apply -f config.yaml

echo ""
echo "Done installing config"

echo ""
echo "Building and importing Docker images..."
echo ""

sudo docker build --no-cache -t imagegrab:latest ./1_imagegrab
sudo docker save -o /tmp/imagegrab.tar imagegrab:latest
sudo ctr images import /tmp/imagegrab.tar
sudo rm /tmp/imagegrab.tar

sudo docker build --no-cache -t resize:latest ./2_resize
sudo docker save -o /tmp/resize.tar resize:latest
sudo ctr images import /tmp/resize.tar
sudo rm /tmp/resize.tar

sudo docker build --no-cache -t grayscale:latest ./3_grayscale
sudo docker save -o /tmp/grayscale.tar grayscale:latest
sudo ctr images import /tmp/grayscale.tar
sudo rm /tmp/grayscale.tar

sudo docker build --no-cache -t objectdetect:latest ./4_objectdetect
sudo docker save -o /tmp/objectdetect.tar objectdetect:latest
sudo ctr images import /tmp/objectdetect.tar
sudo rm /tmp/objectdetect.tar

sudo docker build --no-cache -t tag:latest ./5_tag
sudo docker save -o /tmp/tag.tar tag:latest
sudo ctr images import /tmp/tag.tar
sudo rm /tmp/tag.tar

echo ""
echo "Imported images into containerd"
echo ""
echo "Deploying Redis and MinIO..."
echo ""

sudo kubectl apply -f redis.yaml
sudo kubectl apply -f minio.yaml

echo ""
echo "Deployed Redis and MinIO"
echo ""
echo "Deploying services..."
echo ""

sudo kubectl apply -f 1_imagegrab/imagegrab_deployment.yaml
sudo kubectl apply -f 2_resize/resize_deployment.yaml
sudo kubectl apply -f 3_grayscale/grayscale_deployment.yaml
sudo kubectl apply -f 4_objectdetect/objectdetect_deployment.yaml
sudo kubectl apply -f 5_tag/tag_deployment.yaml

echo ""
echo "Deployed services"
echo ""
echo "Installing MinIO client..."
echo ""

sudo curl https://dl.min.io/client/mc/release/linux-amd64/mc -o mc
sudo chmod +x mc
sudo mv mc /usr/local/bin/

echo ""
echo "MinIO client installed"
echo ""
echo "Setting up port forwarding..."
echo ""

sleep 10  # Wait for services to be up
sudo kubectl port-forward service/imagegrab 8080:80 &
sudo kubectl port-forward service/minio 9000:9000 &

echo ""
echo "Port forwarding set up"
echo ""
echo "Setting up MinIO bucket..."
echo ""

sudo mc alias set localminio http://localhost:9000 minioadmin minioadmin
sudo mc mb localminio/images

echo ""
echo "Done MinIO bucket setup"
echo ""
echo "Setting up testing..."
echo ""
sudo chmod +x test.sh
sudo git config --global user.name "hajduko"
sudo git config --global user.email "hajdu.kolos@edu.bme.hu"
ssh-keygen -t ed25519 -C "hajdu.kolos@edu.bme.hu"
cat ~/.ssh/id_ed25519.pub

read -p "Copy the above key to your GitHub SSH keys (https://github.com/settings/keys) and press enter to continue..."

echo "All services deployed!"