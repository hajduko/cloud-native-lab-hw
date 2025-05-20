echo "Testing the setup..."
sudo curl -X POST http://localhost:8080/upload -F "image=@test-1.jpg"
sleep 5
sudo mc ls --recursive localminio/images