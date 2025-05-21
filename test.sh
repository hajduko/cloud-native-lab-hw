echo "Testing the setup..."
sudo curl -X POST http://localhost:8080/upload -F "image=@test-1.jpg"
sleep 5
sudo mc ls --recursive localminio/images
read -p "Enter the uid of the images: " uid
sudo mc get localminio/images/$uid/original.jpg original.jpg
sudo mc get localminio/images/$uid/resized.jpg resized.jpg
sudo mc get localminio/images/$uid/grayscale.jpg grayscale.jpg
sudo mc get localminio/images/$uid/result.jpg result.jpg
sudo git add .
sudo git commit -m "$uid"
<<<<<<< HEAD
echo "Test images commited to GitHub"
=======
sudo git push
echo "Test images pushed to GitHub"
>>>>>>> 9c8a882c9f3080ca90f111c015f2a5c3d63e088e
