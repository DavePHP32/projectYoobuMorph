#git pull origin main
source .env.deploy

echo $DOCKER_HUB_PASSWORD | docker login -u $DOCKER_HUB_USERNAME --password-stdin

docker build -t moussasamina/yoobu-morph:latest .

docker image push moussasamina/yoobu-morph:latest
