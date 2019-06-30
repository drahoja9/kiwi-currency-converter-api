#!/bin/bash

echo 'Logging in Docker...'
docker login -u "$DOCKER_USERNAME" -p "$DOCKER_PASSWORD"

echo 'Pushing to Docker Hub...'
docker push drahoja9/kiwi-currency-converter-api:latest
echo 'Successfully pushed!'