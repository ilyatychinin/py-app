#!/bin/bash

set -e

echo "выполняем гит пул"
git pull origin main

echo "останавливаем сервисы"
docker compose down -v 
sleep 3

echo "собираем новый имэдж"
docker compose build 

echo "запускаем приложение"
docker compose up -d
sleep 2

echo "Работающие контейнеры"
docker compose ps
