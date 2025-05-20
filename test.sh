echo "Testing the setup..."
sudo curl -X POST http://localhost:8080/upload -F "image=@test-1.jpg"
sudo uid=$(mc ls localminio/images | awk '{print $5}' | tr -d '/')
sudo mc ls localminio/images/$uid