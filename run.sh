PROJECT_NAME=telegramboostservice

docker kill $PROJECT_NAME
docker rm $PROJECT_NAME
docker rmi $PROJECT_NAME

docker build -t $PROJECT_NAME .
docker run -ti --restart=always -v $PROJECT_NAME:/data --name $PROJECT_NAME $PROJECT_NAME