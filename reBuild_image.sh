#!/bin/bash

set -e 

IMAGE_VERSION=v3
CONTAINER_NAME=py-app
docker container ls
echo "Остановка старого контейнера"
docker container kill $CONTAINER_NAME

echo "Удаление старого контейнера"
docker container rm $CONTAINER_NAME

echo "Удаление старого image"
docker image rm py-app:$IMAGE_VERSION

echo "Создание нового image"
docker image build -f Dockerfile.dev -t py-app:$IMAGE_VERSION . 

echo "Скрипт выполнился успешно!"
