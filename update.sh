#!/bin/bash

OLD_IMAGE_ID=$(docker images --filter=reference=usagi12 --format "{{.ID}}")
docker rm -f usagi12

git pull
./build.sh
./start.sh

docker rmi "$OLD_IMAGE_ID"